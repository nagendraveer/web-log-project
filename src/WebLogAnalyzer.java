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

public class WebLogAnalyzer {


public static class StatusMapper
        extends Mapper<LongWritable, Text, Text, IntWritable> {

    private static final Pattern STATUS_PATTERN =
            Pattern.compile("\"\\S+\\s+\\S+\\s+HTTP/[^\"]+\"\\s+(\\d{3})\\s+\\S+");

    private final Text statusCode = new Text();
    private static final IntWritable ONE = new IntWritable(1);

    @Override
    public void map(LongWritable key, Text value, Context context)
            throws IOException, InterruptedException {

        Matcher matcher = STATUS_PATTERN.matcher(value.toString());

        if (matcher.find()) {
            statusCode.set(matcher.group(1));
            context.write(statusCode, ONE);
        }
    }
}

public static class StatusReducer
        extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final IntWritable result = new IntWritable();

    @Override
    public void reduce(Text key, Iterable<IntWritable> values,
                       Context context)
            throws IOException, InterruptedException {

        int sum = 0;

        for (IntWritable value : values) {
            sum += value.get();
        }

        result.set(sum);
        context.write(key, result);
    }
}

public static void main(String[] args) throws Exception {

    if (args.length != 2) {
        System.err.println(
                "Usage: WebLogAnalyzer <input path> <output path>");
        System.exit(2);
    }

    Configuration conf = new Configuration();

    Job job = Job.getInstance(conf, "NASA Web Log Status Analysis");

    job.setJarByClass(WebLogAnalyzer.class);

    job.setMapperClass(StatusMapper.class);
    job.setCombinerClass(StatusReducer.class);
    job.setReducerClass(StatusReducer.class);

    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);

    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));

    System.exit(job.waitForCompletion(true) ? 0 : 1);
}


}
