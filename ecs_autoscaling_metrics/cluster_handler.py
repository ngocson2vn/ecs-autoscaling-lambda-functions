import os
import sys
import datetime
import traceback

sys.path.append("./vendored")
import slackweb
from cloudwatch import cloudwatch


ECS_CLUSTERS = [x.strip() for x in os.environ['ECS_CLUSTERS'].split(',')]
SLACK_URL = os.environ.get('SLACK_URL')


def normalize(cpu, mem, mem_rsv):
	if mem_rsv > 95:
		return 50 + (cpu + mem + mem_rsv)            # 100 <  value         ==> scale out
	elif cpu < 30 and mem < 30 and mem_rsv < 85:
		return (cpu + mem)                           #  60 >  value         ==> scale in
	elif cpu < 30 and mem < 30 and mem_rsv >= 85:
		return 90
	elif cpu > 50 or mem > 50:  
		return 50 + (cpu + mem)                      # 100 <  value         ==> scale out
	else:
		return (cpu + mem)                           #  60 <= value <= 100  ==> stable zone


def normalize_cpu_mem(a, b):
	end_time = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=1)
	start_time = end_time - datetime.timedelta(minutes=1)
	print("StartTime: {}".format(start_time))
	print("EndTime: {}".format(end_time))

	for cluster_name in ECS_CLUSTERS:
		try:
			cpu = cloudwatch.get_cluster_metric_value(cluster_name, 'CPUUtilization', start_time, end_time)
			mem = cloudwatch.get_cluster_metric_value(cluster_name, 'MemoryUtilization', start_time, end_time)
			mem_rsv = cloudwatch.get_cluster_metric_value(cluster_name, 'MemoryReservation', start_time, end_time)
			print("ClusterName: {}, CPUUtilization: {}, MemoryUtilization: {}, MemoryReservation: {}".format(cluster_name, cpu, mem, mem_rsv))

			if cpu is not None and mem is not None:
				metric_value = normalize(cpu, mem, mem_rsv)
				print("ClusterName: {}, CPUMemoryUtilizationNormalized: {}".format(cluster_name, metric_value))

				cloudwatch.publish_custom_metric('ClusterName', cluster_name, 'CPUUtilization', cpu, 'Percent', start_time)
				cloudwatch.publish_custom_metric('ClusterName', cluster_name, 'MemoryUtilization', mem, 'Percent', start_time)
				cloudwatch.publish_custom_metric('ClusterName', cluster_name, 'CPUMemoryUtilizationNormalized', metric_value, 'Percent', start_time)
		except Exception as ex:
			tb = traceback.format_exc()
			slack = slackweb.Slack(url=SLACK_URL)
			err = "*[ecs-autoscaling-metrics-production-normalize_cpu_mem]*\n{}".format(tb)
			print(err)
			slack.notify(text=err)
