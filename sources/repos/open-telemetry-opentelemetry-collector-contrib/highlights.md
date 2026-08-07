# Highlights

- `Overview_and_Architecture.md:L13-L21` Contrib supplies community integrations, while official distribution manifests live in a separate releases repository.
- `OTTL_Transformation_Language.md:L1-L9` OTTL expresses telemetry edits as function calls with optional conditional `where` clauses.
- `Kubernetes_and_Container_Observability.md:L100-L104` DaemonSets suit node-local collection, while Deployments suit cluster-wide services.
- `Resource_Detection_and_Metadata_Enrichment.md:L78-L131` The resource detection processor runs ordered, pluggable detectors and caches their results.
- `Observer_Pattern_and_Dynamic_Receiver_Creation.md:L1-L9` Observers emit endpoint changes that rules turn into dynamically started or stopped receivers.
- `OpAMP_Supervisor_for_Agent_Management.md:L9-L17` The Supervisor bridges a remote OpAMP backend and the locally managed Collector.
- `OpAMP_Supervisor_for_Agent_Management.md:L172-L192` Remote configuration changes produce a new effective config and a reload or restart verified through health feedback.
- `Component_Lifecycle_and_Stability_Management.md:L7-L18` Stability is declared per telemetry signal rather than once for an entire component.
- `Component_Lifecycle_and_Stability_Management.md:L92-L132` Component metadata drives generated runtime constants, tests, ownership, and issue configuration.
- `Authentication_Extensions.md:L1-L5` Shared authentication interfaces decouple inbound verification and outbound credential injection from receivers and exporters.
- `Authentication_Extensions.md:L172-L185` Storage extensions expose scoped clients so components can persist checkpoints and queues without depending on a backend.
