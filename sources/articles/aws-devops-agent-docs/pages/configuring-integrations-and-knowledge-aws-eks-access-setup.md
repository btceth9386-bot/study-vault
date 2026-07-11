

# AWS EKS access setup
<a name="configuring-integrations-and-knowledge-aws-eks-access-setup"></a>

You can enable AWS DevOps Agent to investigate issues in your Amazon EKS clusters by running read-only `kubectl` commands against both public and private clusters. You can connect any number of EKS clusters to the same Agent Space.

Once connected, the agent can help diagnose operational issues in your clusters — describing resources, retrieving pod logs, inspecting cluster events, checking node health, and more. The agent cannot create, modify, or delete any resources in your cluster.

## Prerequisites
<a name="prerequisites"></a>

Before setting up EKS access, ensure that your EKS cluster's authentication mode includes the EKS API. You can check this on the **Access** tab in the [Amazon EKS console](https://console.aws.amazon.com/eks). If the mode doesn't include the EKS API, select a mode that does before proceeding.

## Setup
<a name="setup"></a>

These steps need to be completed from the [Amazon EKS console](https://console.aws.amazon.com/eks) for each cluster you wish to create an access entry for. You can find your IAM role ARN in your Agent Space (see [Creating an Agent Space](getting-started-with-aws-devops-agent-creating-an-agent-space.md)) under **Capabilities > Cloud > Primary Source > Edit**.

1. Go to the **Access** tab. If the Authentication mode already says EKS API, you can add access entries. Otherwise, select a mode that includes the EKS API.

1. From the Access tab, create a new IAM access entry. Copy your primary cloud source IAM role ARN and enter it as the IAM principal for the access entry. Choose **Next**.

1. Select the AWS Managed **AmazonAIOpsAssistantPolicy** access policy, and select **Cluster** for the access scope. (Alternatively, if you'd like the agent to only access certain namespaces, select the desired **Kubernetes Namespaces**). Choose **Add Policy**, and then choose **Next**.

1. Review the changes and confirm that the correct access entry policy and IAM role were chosen, and create your access entry by choosing **"Create"**.

To verify that the EKS access was configured correctly, navigate to the Operator App and start a new investigation, asking the agent a question about your cluster, such as "list all pods in the default namespace" or "show me recent events in my cluster".

## Troubleshooting
<a name="troubleshooting"></a>

If the agent can't reach your cluster, verify that the access entry is using the correct IAM role ARN shown in the setup dialog and that the **AmazonAIOpsAssistantPolicy** access policy is attached.