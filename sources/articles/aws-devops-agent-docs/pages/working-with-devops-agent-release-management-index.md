

# Release management
<a name="working-with-devops-agent-release-management-index"></a>

**Preview:** Release management capabilities are currently in preview and available only in US East (N. Virginia) `us-east-1`. Support for all AWS DevOps Agent [Supported Regions](about-aws-devops-agent-supported-regions.md) will be added at general availability.

Release management is the automated validation layer between code generation and production deployment. AWS DevOps Agent reviews your code changes for standards adherence, cross-codebase dependency risks, and access-control correctness — then verifies behavior through autonomous release testing — so issues are caught and resolved before they reach production.

## Release management capabilities
<a name="release-management-capabilities"></a>

Release management includes two core capabilities:
+ **Release readiness code review** — Automated evaluation of code changes against your organization's policies, cross-repository dependency analysis, and access-control verification. Reviews can run during code generation, in pull requests and merge requests, or on-demand through chat. See [Release readiness code reviews](release-management-release-readiness-code-review.md).
+ **Release testing** — Automatic generation and execution of tests to validate code behavior before deployment. The agent analyzes your change, determines what needs testing, and runs tests against a deployed instance of your application. See [Release testing](release-management-release-testing.md).

## Release readiness code review
<a name="release-readiness-code-review"></a>

Release readiness code review evaluates your code changes for policy compliance, cross-repository dependency risks, and access-control correctness. Unlike standard linting or static analysis, these reviews understand your application's architecture, its relationships with other repositories, and your organization's policies to surface issues that would cause production failures.

The agent assesses changes through multiple lenses:
+ **Standards evaluation** — Assesses the change against your organization's standards and best practices, defined as natural-language Skills. Policies can cover security, reliability, performance, and operational best practices without requiring policy-as-code expertise.
+ **Cross-repository dependency analysis** — Maps how your repositories interact and identifies when a change in one repository will break consumers in another, using a knowledge graph built from indexing your connected repositories.
+ **Access-control verification** — For CloudFormation changes, verifies that IAM policies, resource policies, and network configurations follow well architected best practices.

Each review produces a report with a recommended action (BLOCK, Proceed with Caution, or Safe to Release), a changes summary, specific risk findings with affected code locations, and actionable recommendations. For more information, see [Release readiness code reviews](release-management-release-readiness-code-review.md).

## Release testing
<a name="release-testing"></a>

Release testing generates and executes tests against a running instance of your application to validate code changes before they reach production. The agent analyzes your code changes, determines what needs testing, generates change-specific test plans, and runs them against your deployed application — all without manual test authoring.

Key aspects of release testing:
+ **Change-specific test plans** — Tests target risk areas surfaced during the release readiness code review rather than running a static regression suite. The agent determines what to test based on what changed.
+ **Real environment execution** — Tests run against a deployed instance of your application in a customer-provisioned environment, catching integration failures and regressions that unit tests miss.
+ **Multiple test types** — Covers functional correctness, UX validation for web applications, API contract testing, and integration behavior across services.
+ **CI/CD integration** — Can be triggered from your IDE, through DevOps Agent chat, or as a stage in GitHub Actions and GitLab CI pipelines.

For more information, see [Release testing](release-management-release-testing.md).

## Where release management runs
<a name="where-release-management-runs"></a>

Release management integrates into your workflow at multiple points:
+ **During code generation** — Inline in Kiro IDE and Claude Code as code is being written, catching issues before code is ever committed.
+ **In pull requests and merge requests** — Automatically triggered when PRs/MRs are opened or updated in GitHub and GitLab. Findings appear as inline comments with recommended fixes.
+ **On-demand** — Through DevOps Agent chat, where you can request reviews of any branch, commit, or repository and ask follow-up questions about findings.

## Getting started with release management
<a name="getting-started-with-release-management"></a>

To begin using release management capabilities:

1. **Connect your repositories** — In your Agent Space, [Connecting to CI/CD pipelines](configuring-integrations-and-knowledge-connecting-to-cicd-pipelines-index.md). The agent will index your code to build a knowledge graph of cross-repository dependencies. Initial indexing takes approximately one to two hours.

1. **Define your policies (optional)** — [Agent instructions](about-aws-devops-agent-agent-instructions.md) to define your desired code review behaviors and internal standards you'd like to have every code review include. You can specify what constitutes a blocking change versus a warning.

1. **Trigger your first review** — Use DevOps Agent chat to request a release readiness review: "Review branch main on repo my-service for release risks." The agent will evaluate the change and return a report with findings.

## How release management learns
<a name="how-release-management-learns"></a>

Release management improves over time through two mechanisms:

1. **Repository knowledge** — As the agent indexes your repositories, it builds an increasingly complete understanding of cross-repository dependencies, shared resources, API contracts, and infrastructure relationships. This knowledge makes dependency risk analysis more accurate with each review.

1. **Customer-provided skills** — Define custom [DevOps Agent Skills](about-aws-devops-agent-devops-agent-skills.md) that encode your organization's specific approaches to evaluating code, such as how to assess cross-service dependencies, when a feature flag is required, which patterns warrant additional scrutiny, or how to evaluate changes against your internal architectural standards. These skills let you teach the agent your team's policies and practices so reviews reflect your organization's expectations.