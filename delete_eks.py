response = client.delete_cluster(
        name = 'clusterdivine2'
)

response2 = client.delete_nodegroup(
        clusterName = 'clusterdivine2',
        nodegroupName = 'divinenode'
)
