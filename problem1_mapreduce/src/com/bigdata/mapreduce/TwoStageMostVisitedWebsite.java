package com.bigdata.mapreduce;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

/**
 * Enterprise Two-Stage MapReduce Pipeline for Large-Scale Data:
 * 
 * Job 1: Distinct User Aggregation per Website
 * Job 2: Global Maximum Extraction
 */
public class TwoStageMostVisitedWebsite extends Configured implements Tool {

    // ==========================================
    // STAGE 1: Calculate Unique Users per Website
    // ==========================================
    public static class Stage1Mapper extends Mapper<LongWritable, Text, Text, Text> {
        private Text websiteKey = new Text();
        private Text userIdVal = new Text();

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty() || line.startsWith("#") || line.startsWith("Website")) return;

            String[] tokens = line.split("[,\\t\\s]+");
            if (tokens.length >= 2) {
                String token0 = tokens[0].trim();
                String token1 = tokens[1].trim();

                String website = token0;
                String userId = token1;
                if (token0.matches("(?i)^(user|u)\\d+.*") && !token1.matches("(?i)^(user|u)\\d+.*")) {
                    userId = token0;
                    website = token1;
                }
                websiteKey.set(website.toLowerCase());
                userIdVal.set(userId);
                context.write(websiteKey, userIdVal);
            }
        }
    }

    public static class Stage1Reducer extends Reducer<Text, Text, Text, IntWritable> {
        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            Set<String> uniqueUsers = new HashSet<>();
            for (Text val : values) {
                uniqueUsers.add(val.toString().trim());
            }
            context.write(key, new IntWritable(uniqueUsers.size()));
        }
    }

    // ==========================================
    // STAGE 2: Global Max Identification
    // ==========================================
    public static class Stage2Mapper extends Mapper<LongWritable, Text, Text, Text> {
        private static final Text DUMMY_KEY = new Text("GLOBAL_MAX");

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty()) return;

            String[] tokens = line.split("[\\t,]+");
            if (tokens.length >= 2) {
                String website = tokens[0].trim();
                String count = tokens[1].trim();
                context.write(DUMMY_KEY, new Text(website + ":" + count));
            }
        }
    }

    public static class Stage2Reducer extends Reducer<Text, Text, Text, IntWritable> {
        @Override
        protected void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            String maxWebsite = null;
            int maxCount = -1;

            for (Text val : values) {
                String[] parts = val.toString().split(":");
                if (parts.length == 2) {
                    String website = parts[0];
                    int count = Integer.parseInt(parts[1]);
                    if (count > maxCount) {
                        maxCount = count;
                        maxWebsite = website;
                    }
                }
            }

            if (maxWebsite != null) {
                context.write(new Text("MAXIMUM_VISITED_WEBSITE: " + maxWebsite), new IntWritable(maxCount));
            }
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        Configuration conf = getConf();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();

        if (otherArgs.length < 2) {
            System.err.println("Usage: TwoStageMostVisitedWebsite <input path> <output path>");
            return -1;
        }

        Path inputPath = new Path(otherArgs[0]);
        Path finalOutputPath = new Path(otherArgs[1]);
        Path intermediatePath = new Path(otherArgs[1] + "_stage1_counts");

        FileSystem fs = finalOutputPath.getFileSystem(conf);
        if (fs.exists(intermediatePath)) {
            fs.delete(intermediatePath, true);
        }
        if (fs.exists(finalOutputPath)) {
            fs.delete(finalOutputPath, true);
        }

        // Job 1
        Job job1 = Job.getInstance(conf, "Job 1: Unique User Count Per Website");
        job1.setJarByClass(TwoStageMostVisitedWebsite.class);
        job1.setMapperClass(Stage1Mapper.class);
        job1.setReducerClass(Stage1Reducer.class);
        job1.setOutputKeyClass(Text.class);
        job1.setOutputValueClass(Text.class);
        FileInputFormat.addInputPath(job1, inputPath);
        FileOutputFormat.setOutputPath(job1, intermediatePath);

        if (!job1.waitForCompletion(true)) {
            return 1;
        }

        // Job 2
        Job job2 = Job.getInstance(conf, "Job 2: Global Maximum Website Finder");
        job2.setJarByClass(TwoStageMostVisitedWebsite.class);
        job2.setMapperClass(Stage2Mapper.class);
        job2.setReducerClass(Stage2Reducer.class);
        job2.setNumReduceTasks(1);
        job2.setOutputKeyClass(Text.class);
        job2.setOutputValueClass(Text.class);
        FileInputFormat.addInputPath(job2, intermediatePath);
        FileOutputFormat.setOutputPath(job2, finalOutputPath);

        return job2.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        int res = ToolRunner.run(new Configuration(), new TwoStageMostVisitedWebsite(), args);
        System.exit(res);
    }
}
