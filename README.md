# ECR-POS
## The general scheme
⋅⋅⋅The integration concerns three systems: ECR, MELLON POS and BANK:

![General Scheme](https://github.com/arbdoescode/ECR-POS/blob/main/images/GeneralScheme.PNG "General Scheme")

⋅⋅⋅The usual flow of communication follows 4 steps:
1. The transactions starts from ECR: the operator selects “payment with card” as form
of payment and ECR sends the corresponding request to POS.
2. POS immediately confirms to ECR the reception of the request and ECR enters into
state to wait for the outcome.
3. POS connects to the bank to ask online authorization or approves the transaction
offline or declines it offline or interrupts the transaction.
4. POS replies to ECR with the final outcome: declined or approved. In case of approval,
POS sends complementary information (transaction number, approval code etc)

## Physical Connections
### CONNECTION OVER TCP/IP
⋅⋅⋅The integration concerns three systems: ECR, MELLON POS and BANK:
![Conn Ip](https://github.com/arbdoescode/ECR-POS/blob/main/images/ConnectionTCP-IP.PNG "Connection Ip")

POS acts as “server” in relation to the ECR and as “client” in relation to the bank. The LAN
switch can be external device or embedded in the cashier machine.
Last chapter provides instructions about how to set up the connection for each POS type.

### CONNECTION OVER USB
⋅⋅⋅This connection is not supported in Axium devices. The connection over USB is also
supported, without any change in the protocol. However, that solution is not widely available
in the existing POS applications.
![Conn Usb](https://github.com/arbdoescode/ECR-POS/blob/main/images/ConnectionUSB.PNG "Connection USB")

## Syntax of the Messages
### Message [ECHO]
It is sent by ECR and initiated by the operator to check the connection with the POS (usually
during the installation). Τhe terminal ID and the POS application version use also to be
completed in the echo message:

**ECR REQUEST:**
```
`X/`<text>
```

**POS RESPONSE:**
```
`X/`<text>`/T`<tid>:<app-version>
```