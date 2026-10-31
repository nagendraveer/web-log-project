import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class HTTPErrorAnalyzer {


public static class ErrorMapper
        extends Mapper<LongWritable, Text, Text, IntWritable> {

    private static final Pattern LOG_PATTERN =
            Pattern.compile("^(\\S+)\\s+\\S+\\s+\\S+\\s+\\[[^]]+\\]\\s+\"[^\"]*\"\\s+(\\d{3})\\s+\\S+");

    private final Text outputKey = new Text();
    private static final IntWritable ONE = new IntWritable(1);

    @Override
    public void map(LongWritable key, Text value, Context context)
            throws IOException, InterruptedException {

        Matcher matcher = LOG_PATTERN.matcher(value.toString());

        if (matcher.find()) {

            String client = matcher.group(1);
            int statusCode = Integer.parseInt(matcher.group(2));

            // Count only HTTP error responses.
            if (statusCode == 403 ||
                statusCode == 404 ||
                statusCode == 500 ||
                statusCode == 501) {

                outputKey.set(client + "\t" + statusCode);
                context.write(outputKey, ONE);
            }
        }
    }
}

public static class ErrorReducer
        extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final IntWritable result = new IntWritable();

    @Override
    public void reduce(Text key, Iterable<IntWritable> values,
                       Context context)
            throws IOException, InterruptedException {

        int total = 0;

        for (IntWritable value : values) {
            total += value.get();
        }

        result.set(total);
        context.write(key, result);
    }
}

public static void main(String[] args) throws Exception {

    if (args.length != 2) {
        System.err.println(
                "Usage: HTTPErrorAnalyzer <input path> <output path>");
        System.exit(2);
    }

    Configuration conf = new Configuration();

    Job job = Job.getInstance(conf, "HTTP Error Analysis");

    job.setJarByClass(HTTPErrorAnalyzer.class);

    job.setMapperClass(ErrorMapper.class);
    job.setCombinerClass(ErrorReducer.class);
    job.setReducerClass(ErrorReducer.class);

    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);

    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));

    System.exit(job.waitForCompletion(true) ? 0 : 1);
}


}
