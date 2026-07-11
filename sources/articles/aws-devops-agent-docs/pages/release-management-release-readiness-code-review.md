

# Release readiness code reviews
<a name="release-management-release-readiness-code-review"></a>

Release readiness code reviews evaluate your code changes for cross-repository dependency risks, internal standards compliance, and access-control correctness. It also performs automated verification testing – it builds, runs, and tests your code changes – in a verification environment managed by the AWS DevOps Agent.

## Getting started
<a name="getting-started"></a>

To use release readiness code reviews, complete the following setup steps.

### Step 1: Enable capabilities on your repositories
<a name="step-1-enable-capabilities-on-your-repositories"></a>

Code review and automated testing capabilities must be enabled on your connected GitHub or GitLab repositories before they can trigger.

The **Code Review and Automated Testing** section in your pipeline provider integration settings provides two per-repository capabilities:
+ **Auto trigger change review** — When enabled, DevOps Agent automatically runs a release readiness code review each time a pull request or merge request is opened or updated. Review findings appear as inline comments on the PR/MR.
+ **Automated verification testing** — When enabled, DevOps Agent builds, runs, and tests your code changes in a managed verification environment during code reviews. This provides functional validation beyond static analysis. For more information, see [Automated verification testing](#automated-verification-testing).

You can enable or disable each capability independently per repository, allowing you to use change reviews without verification testing or vice versa.

The section also includes:
+ **Runtime role** (optional) — Choose the IAM role that DevOps Agent assumes to run automated capabilities on your selected repositories. This role is used when accessing internal services during builds, such as private package registries or artifact stores. For more information, see [Step 2](#step-2-configure-private-vpc-access-for-the-verification-testing-environment-optional).

**For GitHub:** Navigate to the **Code Review and Automated Testing** section in your GitHub integration settings and enable the capabilities for each repository. Both capabilities are enabled by default when you connect repositories. For detailed instructions, see [Configuring Code Review and Automated Testing](connecting-to-cicd-pipelines-connecting-github.md).

**For GitLab:** Navigate to the **Code Review and Automated Testing** section in your GitLab integration settings and enable the capabilities for your projects. For detailed instructions, see [Configuring Code Review and Automated Testing](connecting-to-cicd-pipelines-connecting-gitlab.md).

### Step 2: Configure private VPC access for the verification testing environment (optional)
<a name="step-2-configure-private-vpc-access-for-the-verification-testing-environment-optional"></a>

Release readiness code reviews can perform automated verification testing by building, running, and testing your code changes in a verification environment (see [Automated verification testing](#automated-verification-testing)). If your code build process requires artifacts from internal systems — such as private image repositories (for example, Artifactory, Docker Hub Enterprise), internal build artifact stores, or dependent code repositories — you need to give the verification testing environment access to a VPC that can reach those service endpoints.

By default, the verification testing environment does not have network access to your internal systems. To enable access, create a private connection and associate it with your pipeline provider ([GitHub](connecting-to-cicd-pipelines-connecting-github.md) or [GitLab](connecting-to-cicd-pipelines-connecting-gitlab.md)). The verification testing environment uses the VPC associated with that private connection by creating and managing an ENI inside the VPC, giving the build environment network access to your internal services.

**Note**  
** Integrating with VPCs in your account routes network traffic through your internal routes, following any network restrictions in place.

To configure private VPC access for verification testing:

1. Create a private connection that targets the VPC where your internal build services are reachable. For instructions, see [Connecting to privately hosted tools](configuring-integrations-and-knowledge-connecting-to-privately-hosted-tools.md).

1. Open the AWS DevOps Agent console and navigate to your Agent Space.

1. Go to the **Capabilities** tab and select your pipeline provider (GitHub or GitLab).

1. In the **Code Review and Automated Testing** section, associate the private connection with your pipeline provider by selecting it from the available connections.

1. For the **Runtime role**, select an IAM role that DevOps Agent will assume when accessing internal services during builds. This role must have permission to access AWS Secrets Manager in the same AWS account as your Agent Space. We recommend using a different role from your primary agent role.

1. Choose **Save** to apply your configuration.

Once associated, the verification testing environment will provision an ENI in the private connection's VPC, giving it direct network access to your internal services during code review builds.

## Performing a code review
<a name="performing-a-code-review"></a>

You can request a code review on-demand through DevOps Agent chat:
+ "Review branch feature/payments on repo payment-service for release risks"
+ "Review commit abc123 on repo infrastructure for release readiness"
+ "What release risks exist in the latest changes to repo order-service?"

The agent evaluates the specified scope — a branch, commit, or set of changes — and returns a release readiness report. The report includes:
+ **Recommended action** — BLOCK, Proceed with Caution, or Safe to Release
+ **Changes summary** — What was modified and the scope of impact
+ **Risk analysis** — Specific findings with affected code locations
+ **Recommendations** — Actionable steps to resolve each finding

Reviews typically complete in 8–10 minutes, depending on the size and complexity of the change.

## Automated code reviews
<a name="automated-code-reviews"></a>

Automated code reviews run without manual intervention. They can trigger in two contexts:

### Code reviews during code generation
<a name="code-reviews-during-code-generation"></a>

When using the Kiro Power or Claude Code plugin, the coding agent can invoke a release readiness review as code is being generated. The review evaluates the in-progress changes against your policies and dependencies, surfacing findings directly in the IDE before the code is committed.

If issues are found, the coding agent is notified and can address them immediately — fixing policy violations, correcting over-permissioned IAM policies, or preparing dependent changes in other repositories.

### Code reviews in pull requests and merge requests
<a name="code-reviews-in-pull-requests-and-merge-requests"></a>

When automated PR/MR reviews are enabled, the agent reviews every new pull request and merge request in your connected repositories. Reviews trigger when:
+ A new PR/MR is opened
+ New commits are pushed to an existing PR/MR

Findings appear as inline comments on the affected lines of code, with the overall assessment posted as a PR/MR comment. You can configure whether findings block merges (required status check) or are advisory only.

## Automated verification testing
<a name="automated-verification-testing"></a>

When a release readiness risk assessment is triggered, DevOps Agent creates an AWS-managed verification environment and clones your code into it. The environment runs on dedicated compute resources with network restrictions that limit access to trusted services for build, artifact storage, and retrieval.

DevOps Agent reads your application's code and project files to determine the required build tools and dependencies, then installs them in the verification environment. After successfully building your application, the agent generates a testing plan and runs it to identify functional risks — such as edge cases that might result in failures or unexpected behavior.

Findings from verification testing are included in the final release readiness report alongside standards, dependency, and access-control findings.

You can use [Agent instructions](about-aws-devops-agent-agent-instructions.md) (AGENTS.md) to tune how verification testing is performed — for example, specifying which test commands to run, what constitutes a passing build, or which parts of the application to exercise during verification.

### Allowed network destinations
<a name="allowed-network-destinations"></a>

The verification testing environment has outbound network access restricted to a predefined allowlist. Your application can reach the following domains during validation:


| Domain | Purpose | 
| --- | --- | 
| .amazonaws.com, .aws.amazon.com | AWS services | 
| .public.ecr.aws | Amazon ECR Public | 
| .docker.com, .docker.io | Docker Hub | 
| .github.com, .githubusercontent.com | GitHub | 
| .gitlab.com | GitLab | 
| .npmjs.com, .npmjs.org | npm registry | 
| .pypi.org, .pypi.python.org, .pythonhosted.org | Python Package Index | 
| .crates.io, .rustup.rs | Rust packages | 
| .maven.org, .gradle.org | Java/Gradle packages | 
| .nuget.org | .NET packages | 
| .rubygems.org, .ruby-lang.org | Ruby packages | 
| .golang.org, .pkg.go.dev, .goproxy.io | Go packages | 
| .nodejs.org, .yarnpkg.com | Node.js | 
| .alpinelinux.org, .debian.org, .ubuntu.com, .centos.org, .fedoraproject.org | Linux distribution repositories | 
| .cloudfront.net | CloudFront distributions | 
| .google.com, .googleapis.com | Google APIs | 
| .microsoft.com, .visualstudio.com | Microsoft services | 
| .sourceforge.net, .bitbucket.org | Source hosting | 

**Note**  
** If your application requires network access to domains not on this list, you can connect your verification testing environment to a VPC will cause the agent to use your own network firewall settings, allowing you to configure access to any of the services your application requires.

## Reviewing code review results
<a name="reviewing-code-review-results"></a>

Each code review produces a report accessible in the **Changes** page of the DevOps Agent web app. Reports include:
+ **Finding categories** — Policy violations, dependency risks, access-control issues, and test coverage gaps
+ **Severity levels** — Blocking (must fix before merge), Warning (should address), and Informational (awareness only)
+ **Execution journal** — The full trace of evaluation steps and tools used by the agent, providing transparency into how conclusions were reached

You can also ask follow-up questions in DevOps Agent chat: "Why did the review flag the IAM change in line 42?" or "What repositories depend on the API endpoint I modified?"

## Integrate with Kiro IDE and CLI
<a name="integrate-with-kiro-ide-and-cli"></a>

To use release readiness code reviews in Kiro:

1. Install the DevOps Agent Kiro Power from the Kiro Power marketplace

1. The Power includes Skills that instruct the coding agent when to invoke release readiness reviews — after significant code changes and before creating a PR

1. Findings surface directly in the IDE, and Kiro will offer to fix identified issues

From the Kiro CLI, you can also trigger reviews explicitly: the coding agent will invoke the release readiness review and incorporate findings into its workflow.

## Integrate with Claude Code
<a name="integrate-with-claude-code"></a>

To use release readiness code reviews in Claude Code:

1. Install the DevOps Agent Claude Code plugin

1. The plugin connects Claude Code to your Agent Space and enables the coding agent to invoke release readiness reviews

1. During development, Claude Code can request a review of in-progress changes and address findings before committing

## Integrate with AWS Transform custom
<a name="integrate-with-aws-transform-custom"></a>

To use release readiness code reviews in [AWS Transform custom](https://docs.aws.amazon.com/transform/latest/userguide/custom.html) :

1. Download the AWS DevOps Agent release readiness code reviews skill from the [AWS Transform custom samples repository](https://github.com/aws-samples/aws-transform-custom-samples/tree/main/client-side-skills/devops-agent-release-readiness-code-review) on GitHub.

1. Install the skill into your AWS Transform environment following the instructions in the repository README.

1. Once installed, the skill integrates with AWS Transform's code generation workflow. When Transform generates or modifies code, the skill invokes a release readiness review against the proposed changes.

1. Review findings surface directly in the Transform output. If issues are identified, Transform can address them before finalizing the code change.

## Using code reviews in GitHub
<a name="using-code-reviews-in-github"></a>

Prerequisites: GitHub repository connected to your Agent Space with automated reviews enabled. For setup instructions, see [Configuring Code Review and Automated Testing](connecting-to-cicd-pipelines-connecting-github.md).
+ Reviews appear as inline comments on pull request diffs, with an overall status comment
+ Configure as a required status check to block merges when blocking findings exist
+ The agent reviews all PRs by default; path and branch filtering is configurable in your Agent Space settings

## Using code reviews in GitLab
<a name="using-code-reviews-in-gitlab"></a>

Prerequisites: GitLab project connected to your Agent Space with automated reviews enabled. For setup instructions, see [Configuring Code Review and Automated Testing](connecting-to-cicd-pipelines-connecting-gitlab.md).
+ Reviews appear as inline comments on merge request diffs, with an overall note
+ Configure as a merge request approval rule to require resolution of blocking findings
+ The agent reviews all MRs by default; path and branch filtering is configurable in your Agent Space settings

## Using code reviews in DevOps Agent chat
<a name="using-code-reviews-in-devops-agent-chat"></a>

From DevOps Agent chat, you can:
+ Request reviews of any branch, commit, or repository scope
+ Ask what the agent knows about your project's dependencies: "Which code bases interact with the service in the payments repo?"
+ Ask follow-up questions about specific findings
+ Request the agent generate a fix for an identified issue
+ View the dependency knowledge graph for your connected repositories

## Agentic safety guardrails
<a name="agentic-safety-guardrails"></a>

Release readiness reviews include built-in safety guardrails that prevent common unsafe agent behaviors. These guardrails are always active during the review process. Specific coverage and enforcement behavior may change as the feature evolves. While we aim to cover as many common unsafe behaviors as we can, some behaviors will not have corresponding guardrails in place.

### Credential exposure prevention
<a name="credential-exposure-prevention"></a>

The agent blocks any tool call where the tool input contains common credential patterns in plaintext, such as AWS keys, access tokens and private keys.

### Sensitive file exfiltration detection
<a name="sensitive-file-exfiltration-detection"></a>

The agent scans and blocks shell commands that combine access to sensitive file paths with network operations, preventing data exfiltration attempts.

### Mutative AWS operation blocking
<a name="mutative-aws-operation-blocking"></a>

The agent blocks any AWS API call that would modify your infrastructure. This prevents the review agent from making changes to your AWS environment during analysis. Read-only operations (describe, get, list) are permitted; mutative operations are blocked.

Read-only operations such as `describe_*`, `get_*`, and `list_*` are permitted.

### Sequential phase enforcement
<a name="sequential-phase-enforcement"></a>

Release readiness review phases must execute in sequence. This ensures systematic and thorough evaluation and prevents incomplete assessments from skipped steps.