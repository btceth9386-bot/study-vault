

# Proactive incident prevention
<a name="production-operations-proactive-incident-prevention"></a>

AWS DevOps Agent analyzes patterns across your incident investigations to deliver targeted recommendations that continuously improve your operational posture and prevent future incidents. Access proactive incident prevention through the Improvements page in the Operator Web App.

## How proactive incident prevention works
<a name="how-proactive-incident-prevention-works"></a>

AWS DevOps Agent evaluates recent incident investigations to identify lasting improvements to prevent future incidents and quicken the mean time to detection (MTTD). The agent analyzes multiple incidents to identify recommendations that may prevent whole classes of incidents in the future, focusing on the most impactful recommendations to ensure they are actionable.

By default, the agent automatically runs evaluations weekly. You can pause the schedule if you prefer to run evaluations only on demand. Manual evaluations are always available, which is useful when a recent investigation warrants a quick turnaround on recommended improvements.

The agent identifies improvements across four categories, shown in the Recommendation Categorization chart on the Improvements page:
+ **Observability** – Recommendations to enhance monitoring, alerting, logging, and system visibility to detect issues quicker and more accurately.
+ **Infrastructure** – Recommendations to optimize resource configurations, capacity tuning, and architectural resilience.
+ **Governance** – Recommendations to strengthen deployment processes, pipeline improvements, testing practices, and operational controls.
+ **Code optimization** – Recommendations to improve application code quality, error handling, and code resilience.

This categorization helps you understand where your operational improvements are most needed and allows you to prioritize recommendations based on your team's focus areas.

## Benefits
<a name="benefits"></a>
+ **Prevent recurring incidents** – Address root causes systematically rather than repeatedly responding to the same types of issues
+ **Reduce operational toil** – Free your team from repetitive firefighting to focus on innovation and strategic improvements
+ **Improve system resilience** – Strengthen your infrastructure, observability, and deployment processes based on real incident data
+ **Learn from historical patterns** – Use insights from past incidents to make targeted improvements that have the greatest impact

## Agent summary
<a name="agent-summary"></a>

The Agent Summary in the Improvements page of the Web App provides a description of the outcomes from the last evaluation of recent incidents. The summary explains the number of incident investigations analyzed, which incidents are similar to past ones, and which recommendations were created or updated with new information.

The summary helps you quickly understand what the agent discovered during its most recent evaluation and highlights the most notable recommendations that could have the greatest impact on your operational posture.

## Controlling evaluations
<a name="controlling-evaluations"></a>

You can control when AWS DevOps Agent evaluates incidents and generates recommendations:
+ **Running evaluations manually** – Choose the **Run Now** button in the Improvements page to start an evaluation immediately. This is useful when a recent investigation warrants a quick turnaround on recommended improvements.
+ **Stopping active evaluations** – Choose the **Stop Evaluation** button in the Improvements page to halt an evaluation that is currently in progress.

## Managing recommendations
<a name="managing-recommendations"></a>

AWS DevOps Agent provides recommendations in the Improvements page where you can review and manage them:
+ **Viewing recommendation details** – Choose a recommendation to open the recommendation details page, where you can see more information about the suggested improvement including the incidents that informed the recommendation, the expected impacts, and next steps. For recommendations with code changes, you can also view the agent-ready specification that can be handed to a coding agent for implementation.
+ **Keep** – Choose ‘Keep’ to retain a recommendation in your backlog for tracking. This allows you to monitor which improvements you plan to implement and track their progress.
+ **Discard** – Choose ‘Discard’ to remove a recommendation from your backlog. When you discard a recommendation, you can provide a natural language explanation of why it doesn’t meet your needs. The agent learns from this feedback and uses it to inform future recommendations, ensuring they become more aligned with your operational priorities and requirements over time.
+ **Implemented** – Choose ‘Implemented’ to mark a recommendation as completed. This helps you track which improvements have been applied and allows the agent to measure the effectiveness of its recommendations over time.
+ **Automatic removal** – Recommendations that have not been marked as Keep or Implemented may be removed after approximately 6 weeks if no new incidents would have been prevented by implementing the recommendation. This ensures the Improvements page focuses on the most relevant improvements for your operational challenges.
+ **Recommendation updates** – Existing recommendations are updated when newer incidents are found that would have been prevented by the recommendation. Updates may change the recommendation’s priority or refine the recommendation based on new insights.

## Recommendation prioritization
<a name="recommendation-prioritization"></a>

AWS DevOps Agent automatically ranks your recommendations by priority to help you focus on the most impactful improvements first. The ranking considers your team’s specific context, operational patterns, and the severity of issues each recommendation addresses.

### How prioritization works
<a name="how-prioritization-works"></a>

Each evaluation cycle, the agent ranks your active recommendations (those in a proposed or kept state) using a combination of:
+ **AI-powered ranking** – The agent assesses the relative importance of your top recommendations based on category relevance, incident severity, and operational impact.
+ **Deterministic scoring** – For larger backlogs, the agent applies a priority score based on incident frequency, severity patterns, and recency to ensure consistent ordering beyond the top-ranked items.

The ranked list appears in the Improvements page with a numeric rank position (1 being highest priority). Recommendations that have been discarded or implemented are not ranked.

### Customizing priorities
<a name="customizing-priorities"></a>

You can influence how the agent ranks recommendations by communicating your team’s priorities through the chat interface:
+ **Setting category preferences** – Tell the agent which recommendation categories matter most to your team (for example, "We prioritize observability improvements over infrastructure changes"). The agent stores these preferences and uses them in future ranking evaluations.
+ **Providing context** – Share information about upcoming projects, compliance requirements, or team focus areas. The agent incorporates this context when determining which recommendations should be prioritized.

To update your preferences, use the chat interface and describe your team’s priorities in natural language. The agent will confirm it has understood and will apply your preferences in the next evaluation cycle.

### Rank stability
<a name="rank-stability"></a>

Recommendation ranks may change between evaluation cycles when:
+ New recommendations are added that have higher priority than existing ones
+ Your team’s stated preferences change
+ New incident data strengthens or weakens the case for a recommendation

Recommendations that you have already marked as Keep retain their position in your backlog regardless of rank changes, ensuring your workflow is not disrupted.

## Agent-ready specifications
<a name="agent-ready-specifications"></a>

For recommendations that involve code or configuration changes, AWS DevOps Agent can generate an agent-ready specification. This specification provides a structured document that can be handed directly to a coding agent for implementation.

The specification includes:
+ **Problem statement** – A summary of the issue and its root cause
+ **Solution summary** – A high-level description of the recommended approach
+ **Target repositories** – The specific repositories where changes need to be made
+ **Code changes** – Detailed descriptions of what needs to change and why, with specific file paths and implementation considerations
+ **Test requirements** – What scenarios need to be tested
+ **Implementation plan** – A phased approach to implementing the changes

Agent-ready specifications accelerate implementation by providing coding agents with the context they need to make production-ready changes without requiring extensive back-and-forth with engineers.

## Implementing recommendations
<a name="implementing-recommendations"></a>

To maximize the value of proactive incident prevention recommendations, consider the following practices for acting on them:
+ **Using agent-ready specifications** – For recommendations with code changes, use the generated specification to accelerate implementation by handing it to a coding agent or using it as a detailed guide for manual implementation.
+ **Adding recommendations to your ticket backlog** – Copy recommendations to your team's ticketing system or project management tool to ensure they are prioritized alongside other engineering work.
+ **Prioritizing recommendations based on impact** – Focus first on recommendations that address the most frequent or severe incident types, or those that affect critical systems.
+ **Tracking implementation progress** – Monitor which recommendations have been implemented and measure their effectiveness by observing whether similar incidents decrease over time.
+ **Coordinating with development teams** – Share recommendations with the appropriate teams who own the affected systems, ensuring they have the context and resources needed to implement improvements.