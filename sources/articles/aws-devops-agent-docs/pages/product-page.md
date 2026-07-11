# Frontier agent – AWS DevOps Agent – AWS

## Why AWS DevOps Agent?

AWS DevOps Agent is your always-available teammate that spans software change and operations across AWS, multicloud, and on-prem environments. It reviews code for release readiness and runs autonomous release testing so your team ships to production with confidence. Post-deployment, it autonomously investigates incidents, provides root cause analysis and mitigation steps, and delivers targeted recommendations to reduce recurring issues. It continuously learns your environment, building deep understanding of your services, dependencies, and operational patterns, so release reviews get more relevant, investigations get faster, and recommendations more precise. Ship faster, reduce MTTR, and drive operational excellence.

![Missing alt text value](https://img.youtube.com/vi/fMQfzwS0prQ/maxresdefault.jpg)

## Production Operations Benefits

AWS DevOps Agent is your always-on, autonomous on-call engineer. It begins investigating the moment an alert comes in, whether at 2 AM or during peak hours, to quickly restore your application to optimal performance. AWS DevOps Agent autonomously triages incidents 24/7, providing root cause analysis and actions for resolution. It uses its understanding of your application resources and relationships to quickly understand dependencies and interactions. AWS DevOps Agent streamlines incident response by automatically routing observations, findings, and mitigation steps through your preferred communication channels such as Slack, ServiceNow, and PagerDuty.

AWS DevOps Agent analyzes patterns across historical incidents to provide actionable recommendations that strengthen four key areas: observability, infrastructure optimization, deployment pipeline enhancement, and application resilience. Recommendations include agent-ready specs to hand implementation off to your coding agent or a colleague to update application or infrastructure code. This drives continuous improvement without needing to manage a backlog.

AWS DevOps Agent enables you to access the untapped insights in your operational data by securely integrating with your workflows and observability tools, runbooks, code repositories, and CI/CD pipelines. AWS DevOps Agent offers built-in integrations with observability tools such as Amazon CloudWatch, Dynatrace, Datadog, Grafana, New Relic, and Splunk, and code repositories and CI/CD pipelines like Azure DevOps, GitHub and GitLab. You can extend AWS DevOps Agent beyond its built-in integrations by securely connecting to your own agents via A2A, private or remote MCP servers, enabling integrations with additional tools such as your organization's custom tools, specialized platforms, or proprietary ticketing systems.

Leverage AWS DevOps Agent's deep understanding of your environment to simplify and automate SRE tasks. Beyond just asking questions, query resource health, investigate incident patterns, track deployments, and explore prevention recommendations, all through a natural language interface. Create, save, and share custom charts and reports that help you track operational metrics and communicate insights with your team. Create custom agents that run on a cadence, like a daily database health report that checks slow queries and parameter tuning, or an agent that reviews logs from the past 24 hours and flags anomalies for review.

## Release Management (Preview) Benefits

Ship confidently knowing changes are reviewed before they reach production. AWS DevOps Agent reviews code for release readiness as code is being written and runs autonomous release testing in your production-like environments.

### Assess code change for release readiness

AWS DevOps Agent helps verify code changes are release-ready during code generation by checking adherence to standards, dependency impacts, and access controls. It runs functional verification to confirm your software builds and runs as expected in an AWS-managed verification environment. DevOps Agent maps cross-repository dependencies to surface breaking changes before merge and uses deterministic mathematical verification to assess that infrastructure changes do not drift permissions outside of Well Architected best practices. By understanding your full service topology, it reasons about blast radius and reviews changes in context of the broader system.

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/management-and-governance/approved/images/release-readiness.19c7f25667703600f8200b0deb5ff2d3ed7d4580.jpg)

### Run change-specific tests

AWS DevOps Agent generates and runs change-specific test plans for web and API-based applications in customer-provisioned environments, catching regressions, UX issues, and integration failures before they reach production. Tests target risk areas surfaced during the release readiness review rather than a static regression suite.

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/management-and-governance/approved/images/release-testing.59c5d000f89d3981d033d415af3cb6c6ec7eaa54.jpg)

## Production Operations Customers

### United Airlines

"At United Airlines, we transport more than 500,000 passengers daily. We have about 38,000 Dynatrace OneAgents monitoring across a hybrid cloud environment, more than 500 AWS accounts, 20,000 AWS Lambda functions, Amazon ECS microservices, and numerous other services. At this scale, we previously used multiple tools performing the same functions across different domains, which created gaps and black boxes during troubleshooting. The AWS DevOps Agent with Dynatrace completely changes that. Dynatrace swiftly and accurately detects issues, identifies the responsible application layer, and then the agent investigates further and provides precise steps to resolve the problem — all directly fed into Dynatrace. Instead of initiating an incident call at 3 a.m. and switching between tools, we now have the answers ready—a single pane of glass."

**Jason Eckhart, Principal Engineer, Reliability and Observability, United Airlines**

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/approved/images/United-Airlines_Logo.9b27ed0c1db18944b9f9e628323bb310a21abe69.png)

### T-Mobile

"When AWS introduced DevOps Agent, T-Mobile was at the table from day one. As a design partner, we saw how AWS DevOps Agent can significantly improve root cause analysis across production environments. Our real-world feedback directly influenced how the product evolved. 

Our infrastructure spans multiple clouds and on- premises environments, with application logs centralized in our on-premises Splunk deployment. AWS DevOps Agent's ability to integrate seamlessly with Splunk and analyze logs across these diverse environments has been impactful as we continue to pilot the solution."

**Aravind Manchireddy, SVP, Technology Operations, T-Mobile**

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/product-categories/compute/approved/images/Tmobile_Logo_600x400.1d913b65665ba1dfbc46d702b2386277044d1393.png)

### Western Governors University

Western Governor's University (WGU), a leading online university serving over 191,000 students, was among the first organizations to deploy Amazon DevOps Agent into production, doing so even ahead of the preview launch at re:Invent. As a large-scale Dynatrace user, WGU leverages the DevOps Agent's native Dynatrace integration, enabling Dynatrace Intelligence to automatically route problem records to the Agent for investigation and return enriched findings directly back into Dynatrace.

During a recent production investigation, WGU’s SRE team used the DevOps Agent to analyze a service disruption scenario, reducing total resolution time from an estimated two hours to just 28 minutes—a 77% improvement in MTTR. The Agent quickly pinpointed the root cause within a Lambda function’s configuration, surfacing critical operational knowledge that had previously existed only in undiscovered internal documentation.

"It was able to provide the smoking gun, identified the Lambda was the cause. The investigation had almost flawless metrics that matched what we saw on the front-end." He added, "Yesterday was a huge victory, if we can continue to accelerate discovery, I can't describe how much of a victory that would be for our organization." With plans to leverage the DevOps Agent Skills feature, WGU is on track to compress investigation time even further.

**Angel Marchena, Director of Technical Operations, Western Governors University**

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/product-categories/compute/approved/images/Western-Governors-University-WGU_Logo.dce45f7a5ef0daab64dbed9730a051ddcd6d55ad.png)

### Zenchef

Zenchef is a restaurant technology platform that helps restaurants manage reservations, table operations, digital menus, payments, and guest marketing from a single commission-free system. With a focused DevOps team managing several production environments across multiple business units, they faced a real test when an API integration issue affecting a downstream partner surfaced during a company hackathon, with engineers engaged in the event and nothing significant showing up in monitoring to point them in the right direction.

Rather than pulling engineers off the hackathon, the team brought the issue to DevOps Agent. It worked through the problem systematically, ruling out authentication as a contributing factor, shifting investigation focus to ECS deployments, and ultimately tracing the root cause to a code regression in which a new version failed to handle an unrecognized enum value in the database. The full investigation wrapped in 20-30 minutes, roughly a 75% reduction compared to the 1-2 hours it would have taken manually, and the findings were shared directly with the responsible engineer.

“During the hackathon, we had nearly no available bandwidth to investigate - and we didn’t need it. We’re always trying to be a couple moves ahead, and this kind of proactive investigation just isn’t always possible otherwise. DevOps Agent is enabling new ways of understanding how our platforms behave.”

**Theo Massard, Platform Engineering Manager, Zenchef**

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/product-categories/compute/approved/images/Zenchef_Logo_600x400.0014d957aecdf711a3537b3dbaae616b3e0bff82.png)

## Release Management (Preview) Customers

### TP ICAP

TP ICAP Group is a global provider of financial markets infrastructure and data, operating in 28 countries with over 5,200 employees. The firm has migrated more than 80% of its technology estate to the cloud and is applying AI across its development and operations lifecycle to support scale, resilience, and operational efficiency.

“Change tickets don’t always provide sufficient technical detail to fully assess the impact of a release. We began testing AWS DevOps Agent release management to address this. By analysing code commits directly, it provides a more objective, code-level view of change risk beyond the descriptions provided by change owners.

"In early testing, it has highlighted additional changes and dependencies not captured in tickets – some of which could have affected other services. This is the type of insight that is often only identified after an issue occurs in production.

"Having that visibility up front supports better decision-making on whether and how to proceed with a release. It strengthens production readiness without slowing delivery, which is critical in maintaining the right balance between delivery speed, control, and resilience.”

**Darren Bird, Group Head of Production, TP ICAP**

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/solution-case-studies/approved/images/TPICAP_logo.d9b8ddcb004ae4bcca7b574f02ac4719858a687d.png)

### Deriv

As a regulated trading platform running 24/7, Deriv holds every code change to strict security, encryption, and reliability standards before it reaches production. AWS DevOps Agent release management capability now runs that review automatically on every pull request across our engineering organization and multiple GitHub organizations, enforcing our policies as natural-language rules and returning a clear SAFE, CAUTION, or BLOCK verdict in minutes, a review that typicallyt ook hours, sometimes a full day. In one recent review it caught critical blockers we'd otherwise have missed, including a database permission gap that would have failed silently in production and a memory leak in a long-running service. We're now extending it with the agent's release testing for automated UI and API testing, while its cross- repository dependency graph gives our SRE team faster blast- radius visibility during incidents.

**Ngeo Jia Jun and Nihal Faisal, Senior Engineers, Deriv**

![Missing alt text value](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/product-categories/compute/approved/images/Deriv_Logo.6601e5a078f897feb1bdc6e5c6421cc111de2e8e.png)

## Resources

## Use cases

### Ship AI-generated code reliably

Your coding agents generated 15 PRs overnight across three repositories. AWS DevOps Agent reviews code change against your internal standards, flags dependency conflicts, and checks whether access controls drift outside of Well Architected best practices to help your team ship code reliably and safely.

### Catch regressions

After you commit, AWS DevOps Agent generates change-specific tests targeting risk areas, catches regressions and integration failures in a production-like environment, and reports findings in the pull request to help you ship safely to production.

### Resolve incidents

AWS DevOps Agent autonomously triages incidents and guides teams to rapid resolution. AWS DevOps Agent integrates with observability tools, code repositories, and CI/CD pipelines to correlate and analyze telemetry, code, and deployment data, sharing its hypotheses, observations, and findings. Through systematic investigations, AWS DevOps Agent identifies root cause of issues stemming from system changes, input anomalies, resource limits, component failures, and dependency issues across your entire environment.

### Prevent future operational incidents

AWS DevOps Agent analyzes patterns across historical incidents to provide actionable recommendations that strengthen four key areas: observability, infrastructure optimization, deployment pipeline enhancement, and application resilience.   

### Accelerate on-demand SRE tasks

Get immediate, contextual answers to operational questions without navigating between consoles. Query resource health, investigate incident patterns, track deployments, and explore recommendations through natural conversation. Beyond Q&A, create, save, and share custom charts and reports such as daily ops health summaries or 4xx error trends. Conversation history is maintained so you can build on earlier queries without losing context. Create custom SRE agents that run on a cadence, like a daily database health report that checks slow queries and parameter tuning, or an agent that reviews logs from the past 24 hours and flags anomalies for review.

## Next steps
