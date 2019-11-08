import boto3

def get_cluster_metric_value(clusterName, metricName, startTime, endTime):
	client = boto3.client('cloudwatch')

	response = client.get_metric_statistics(
		Namespace='ECS/Resources',
		MetricName=metricName,
		Dimensions=[
			{
				'Name': 'ClusterName',
				'Value': clusterName
			},
		],
		StartTime=startTime,
		EndTime=endTime,
		Period=60,
		Statistics=[
			'Average'
		],
		Unit='Percent'
	)

	dps = response["Datapoints"]
	if len(dps) > 0:
		return dps[0]["Average"]

	return None
