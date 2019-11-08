import boto3


def get_cluster_metric_value(cluster_name, metric_name, start_time, end_time):
	client = boto3.client('cloudwatch')

	response = client.get_metric_statistics(
		Namespace='AWS/ECS',
		MetricName=metric_name,
		Dimensions=[
			{
				'Name': 'ClusterName',
				'Value': cluster_name
			},
		],
		StartTime=start_time,
		EndTime=end_time,
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

def get_request_count(targetGroup, start_time, end_time):
	client = boto3.client('cloudwatch')

	response = client.get_metric_statistics(
		Namespace='AWS/ApplicationELB',
		MetricName='RequestCountPerTarget',
		Dimensions=[
			{
				'Name': 'TargetGroup',
				'Value': targetGroup
			},
		],
		StartTime=start_time,
		EndTime=end_time,
		Period=60,
		Statistics=[
			'Sum'
		],
		Unit='None'
	)

	dps = response["Datapoints"]
	if len(dps) > 0:
		return dps[0]["Sum"]

	return 0.0

def publish_custom_metric(dimension_name, dimension_value, metric_name, metric_value, unit, timestamp):
	client = boto3.client('cloudwatch')
	response = client.put_metric_data(
		Namespace='ECS/Resources',
		MetricData=[
			{
				'MetricName': metric_name,
				'Dimensions': [
					{
						'Name': dimension_name,
						'Value': dimension_value
					},
				],
				'Timestamp': timestamp,
				'Value': metric_value,
				'Unit': unit
			},
		]
	)