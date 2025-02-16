# Python-Script
# How to Use and Set Up `eks_create.py` and `delete_eks.py`

## **1. Setting Up Your Environment**
1. **Create a Working Directory**
   - Make a new folder to store your scripts and configurations.

2. **Set Up a Virtual Environment**
   ```sh
   python -m venv env
   source env/bin/activate  # On macOS/Linux
   env\Scripts\activate  # On Windows
   ```

3. **Install Required Modules**
   ```sh
   pip install boto3 pyyaml
   ```

## **2. Writing the `eks_create.py` Script**
### **Importing Necessary Modules**
```python
import boto3
import yaml
```

### **Initializing the EKS Client**
We create a client for interacting with Amazon EKS:
```python
client = boto3.client('eks')
```

### **Defining Cluster and NodeGroup Names**
```python
cluster_name = "clusterdivine2"
nodegroup_name = "divinenode"
```

---

## **3. Cluster Creation**
### **What is an EKS Cluster?**
An Amazon EKS cluster is a managed Kubernetes control plane that manages worker nodes and workloads. It provides a scalable and highly available Kubernetes environment on AWS.

### **Cluster Creation with a Try-Except Block**
To avoid errors when rerunning the script, we first check if the cluster exists before creating it.

```python
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
```

### **Code Breakdown:**
#### **Try Block:**
- Calls `describe_cluster()` to check if the cluster exists.
- If the cluster exists, it prints a message and skips creation.

#### **Except Block:**
- If `ResourceNotFoundException` is raised, it means the cluster doesn’t exist, so we proceed to create it.

#### **Parameters:**
- `name`: Name of the cluster.
- `roleArn`: IAM role with the necessary permissions.
- `resourcesVpcConfig`: Specifies the VPC, subnets, and security groups for networking.

---

## **4. Node Group Creation**
### **What is a Node Group?**
A Node Group is a set of worker nodes (EC2 instances) that run Kubernetes workloads in an EKS cluster.

### **Node Group Creation with a Try-Except Block**
```python
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
```

### **Code Breakdown:**
#### **Try Block:**
- Calls `describe_nodegroup()` to check if the node group exists.
- If it exists, it prints a message and skips creation.

#### **Except Block:**
- If `ResourceNotFoundException` is raised, it means the node group doesn’t exist, so we create it.

#### **Parameters:**
- `clusterName`: Name of the cluster the node group belongs to.
- `nodegroupName`: Name of the node group.
- `scalingConfig`: Defines the minimum, maximum, and desired number of nodes.
- `subnets`: List of subnets where the nodes will be launched.
- `instanceTypes`: Specifies EC2 instance type for worker nodes.
- `nodeRole`: IAM role for worker nodes.

---

## **5. Configuring Kubernetes to Interact with EKS**
After creating the cluster and node group, we need to configure `kubectl` to interact with the cluster.

```python
region = "us-east-1"
s = boto3.Session(region_name=region)
eks = s.client("eks")

# Get cluster details
cluster = eks.describe_cluster(name=cluster_name)
cluster_cert = cluster["cluster"]["certificateAuthority"]["data"]
cluster_ep = cluster["cluster"]["endpoint"]

# Build the kubeconfig file
cluster_config = {
    "apiVersion": "v1",
    "kind": "Config",
    "clusters": [{
        "cluster": {
            "server": str(cluster_ep),
            "certificate-authority-data": str(cluster_cert)
        },
        "name": "kubernetes"
    }],
    "contexts": [{
        "context": {
            "cluster": "kubernetes",
            "user": "aws"
        },
        "name": "aws"
    }],
    "current-context": "aws",
    "preferences": {},
    "users": [{
        "name": "aws",
        "user": {
            "exec": {
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "command": "aws-iam-authenticator",
                "args": ["token", "-i", cluster_name]
            }
        }
    }]
}

# Write kubeconfig file
config_file = "kubeconfig.yaml"
config_text = yaml.dump(cluster_config, default_flow_style=False)
with open(config_file, "w") as file:
    file.write(config_text)

print("Kubeconfig file written successfully!")
```

This allows `kubectl` to communicate with the cluster.

---

## **6. Deleting the EKS Cluster and Node Group (`delete_eks.py`)**
To delete the cluster and node group, create a separate script:

```python
client.delete_nodegroup(clusterName='clusterdivine2', nodegroupName='divinenode')
client.delete_cluster(name='clusterdivine2')
print("Cluster and NodeGroup deleted successfully.")
```

---

## **Conclusion**
This guide walks you through setting up, managing, and deleting an AWS EKS cluster using Python and `boto3`. By following these steps, you can automate cluster management efficiently.


