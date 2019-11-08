import boto3


def list_services(cluster_name):
	serviceArns = []
	client = boto3.client('ecs')
	response = client.list_services(cluster=cluster_name)
	nextToken = response['nextToken']
	serviceArns = serviceArns + response['serviceArns']

	while nextToken:
		response = client.list_services(cluster=cluster_name, nextToken=nextToken, maxResults=100)
		serviceArns = serviceArns + response['serviceArns']
		nextToken = response['nextToken'] if 'nextToken' in response else ''

	return serviceArns


def describe_services(cluster_name):
	client = boto3.client('ecs')
	serviceArns = list_services(cluster_name)
	count = len(serviceArns)

	services = []
	start = 0
	end = start + 10
	while start < count:
		if end > count:
			end = count

		resp = client.describe_services(cluster=cluster_name, services=serviceArns[start:end])

		if resp is not None:
			for service in resp['services']:
				if (service['desiredCount'] > 1) and ('loadBalancers' in service) and (len(service['loadBalancers']) > 0):
					tg = service['loadBalancers'][0]['targetGroupArn'].split(':')[5]
					services.append({'serviceName': service['serviceName'], 'desiredCount': service['desiredCount'], 'targetGroup': tg})

		start = start + 10
		end = start + 10

	return services