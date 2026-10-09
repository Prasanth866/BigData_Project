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

public class MostVisitedWebsite extends Configured implements Tool {

    public static class WebsiteTrafficMapper
            extends Mapper<LongWritable, Text, Text, Text> {

        private Text websiteKey = new Text();
        private Text userIdValue = new Text();

        @Override
        public void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            String line = value.toString().trim();
            if (line.isEmpty() || line.startsWith("#") || line.startsWith("Website")) {
                return;
            }

            String[] tokens = line.split("[,\\t\\s]+");
            if (tokens.length >= 2) {
                String token0 = tokens[0].trim();
                String token1 = tokens[1].trim();

                String website;
                String userId;

                if (token0.matches("(?i)^(user|u)\\d+.*") && !token1.matches("(?i)^(user|u)\\d+.*")) {
                    userId = token0;
                    website = token1;
                } else {
                    website = token0;
                    userId = token1;
                }

                websiteKey.set(website.toLowerCase());
                userIdValue.set(userId);
                context.write(websiteKey, userIdValue);
            }
        }
    }

    public static class MostVisitedReducer
            extends Reducer<Text, Text, Text, IntWritable> {

        private Text maxWebsite = new Text("NONE");
        private int maxUserCount = -1;
        private IntWritable resultCount = new IntWritable();

        @Override
        public void reduce(Text key, Iterable<Text> values, Context context)
                throws IOException, InterruptedException {
            Set<String> uniqueUsers = new HashSet<>();

            for (Text val : values) {
                uniqueUsers.add(val.toString().trim());
            }

            int count = uniqueUsers.size();
            resultCount.set(count);
            context.write(key, resultCount);

            if (count > maxUserCount) {
                maxUserCount = count;
                maxWebsite.set(key.toString());
            }
        }

        @Override
        protected void cleanup(Context context) throws IOException, InterruptedException {
            if (maxUserCount >= 0) {
                context.write(new Text("----------------------------------------"), new IntWritable(0));
                context.write(new Text("MAXIMUM_VISITED_WEBSITE: " + maxWebsite.toString()), new IntWritable(maxUserCount));
                context.write(new Text("----------------------------------------"), new IntWritable(0));
            }
        }
    }

    @Override
    public int run(String[] args) throws Exception {
        Configuration conf = getConf();
        String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();

        if (otherArgs.length < 2) {
            System.err.println("Usage: MostVisitedWebsite <input path> <output path>");
            return -1;
        }

        Path inputPath = new Path(otherArgs[0]);
        Path outputPath = new Path(otherArgs[1]);

        FileSystem fs = outputPath.getFileSystem(conf);
        if (fs.exists(outputPath)) {
            fs.delete(outputPath, true);
        }

        Job job = Job.getInstance(conf, "Most Visited Website by Maximum Users");
        job.setJarByClass(MostVisitedWebsite.class);

        job.setMapperClass(WebsiteTrafficMapper.class);
        job.setReducerClass(MostVisitedReducer.class);
        job.setNumReduceTasks(1);

        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        FileInputFormat.addInputPath(job, inputPath);
        FileOutputFormat.setOutputPath(job, outputPath);

        return job.waitForCompletion(true) ? 0 : 1;
    }

    public static void main(String[] args) throws Exception {
        int res = ToolRunner.run(new Configuration(), new MostVisitedWebsite(), args);
        System.exit(res);
    }
}
