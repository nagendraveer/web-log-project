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

public class ClientRequestAnalyzer {


public static class ClientMapper
        extends Mapper<LongWritable, Text, Text, IntWritable> {

    private static final Pattern LOG_PATTERN =
            Pattern.compile("^(\\S+)\\s+\\S+\\s+\\S+\\s+\\[[^]]+\\]\\s+\"[^\\\"]*\"\\s+\\d{3}\\s+\\S+");

    private final Text client = new Text();
    private static final IntWritable ONE = new IntWritable(1);

    @Override
    public void map(LongWritable key, Text value, Context context)
            throws IOException, InterruptedException {

        Matcher matcher = LOG_PATTERN.matcher(value.toString());

        if (matcher.find()) {
            client.set(matcher.group(1));
            context.write(client, ONE);
        }
    }
}

public static class ClientReducer
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
                "Usage: ClientRequestAnalyzer <input path> <output path>");
        System.exit(2);
    }

    Configuration conf = new Configuration();

    Job job = Job.getInstance(conf, "NASA Client Request Analysis");

    job.setJarByClass(ClientRequestAnalyzer.class);

    job.setMapperClass(ClientMapper.class);
    job.setCombinerClass(ClientReducer.class);
    job.setReducerClass(ClientReducer.class);

    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);

    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));

    System.exit(job.waitForCompletion(true) ? 0 : 1);
}


}
