import boto3
import yaml

client = boto3.client('eks')

cluster_name = "clusterdivine2"
nodegroup_name = "divinenode"

# Check if cluster exists
try:
    response = client.describe_cluster(name=cluster_name)
    print(f"Cluster '{cluster_name}' already exists. Skipping creation.")
except client.exceptions.ResourceNotFoundException:
    print(f"Cluster '{cluster_name}' does not exist. Creating...")
    response = client.create_cluster(
        name=cluster_name,
        roleArn='arn:aws:iam::637423435427:role/divine-cluster-role',
        resourcesVpcConfig={
            'subnetIds': ['subnet-0c3c4f79cdf567cb1', 'subnet-043aa8b18f5f2f88b'],
            'securityGroupIds': ['sg-06be4b457a0e7597e'],
        }
    )
    print("Cluster creation started:", response)

# Check if NodeGroup exists
try:
    response_node = client.describe_nodegroup(clusterName=cluster_name, nodegroupName=nodegroup_name)
    print(f"NodeGroup '{nodegroup_name}' already exists. Skipping creation.")
except client.exceptions.ResourceNotFoundException:
    print(f"NodeGroup '{nodegroup_name}' does not exist. Creating...")
    response_node = client.create_nodegroup(
        clusterName=cluster_name,
        nodegroupName=nodegroup_name,
        scalingConfig={
            'minSize': 1,
            'maxSize': 1,
            'desiredSize': 1
        },
        subnets=['subnet-0c3c4f79cdf567cb1', 'subnet-043aa8b18f5f2f88b'],
        instanceTypes=['t2.micro'],
        nodeRole='arn:aws:iam::637423435427:role/eks-nodegroup-role'
    )
    print("NodeGroup creation started:", response_node)

# Set up the client
region = "us-east-1"
s = boto3.Session(region_name=region)
eks = s.client("eks")

# Get cluster details
cluster = eks.describe_cluster(name=cluster_name)
cluster_cert = cluster["cluster"]["certificateAuthority"]["data"]
cluster_ep = cluster["cluster"]["endpoint"]

# Build the cluster config hash
cluster_config = {
    "apiVersion": "v1",
    "kind": "Config",
    "clusters": [
        {
            "cluster": {
                "server": str(cluster_ep),
                "certificate-authority-data": str(cluster_cert)
            },
            "name": "kubernetes"
        }
    ],
    "contexts": [
        {
            "context": {
                "cluster": "kubernetes",
                "user": "aws"
            },
            "name": "aws"
        }
    ],
    "current-context": "aws",
    "preferences": {},
    "users": [
        {
            "name": "aws",
            "user": {
                "exec": {
                    "apiVersion": "client.authentication.k8s.io/v1beta1",
                    "command": "aws-iam-authenticator",
                    "args": [
                        "token", "-i", cluster_name
                    ]
                }
            }
        }
    ]
}

# Write in YAML
config_file = "kubeconfig.yaml"  # Make sure config_file is defined
config_text = yaml.dump(cluster_config, default_flow_style=False)
with open(config_file, "w") as file:
    file.write(config_text)

print("Kubeconfig file written successfully!")
