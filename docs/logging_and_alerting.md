# Logging and alerting

The UNICell storage system generates the following logs that are visible to the administrator :

**Audit trail** : For any modification to the UNICell system from IntegralView, an audit trail entry is created documented the time, the action and the source IP from where this change was done. This is useful in tracking the usage and modification history of the system.

**Alerts** : The UNICell system monitors the health of all components every minute and if it finds any problems in any of its major components, it generate an alert. You can also configure the system to send an email every time an alert is generated. Please see the “System configuration” section for details on how to do this.

**System logs** : These comprise the underlying operating system logs along with the CIFS services logs. These logs can be downloaded in a compressed format onto your computer.