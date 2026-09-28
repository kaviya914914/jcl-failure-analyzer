\# jcl-failure-analyzer



A Python tool that reads mainframe job logs, finds every abend, and explains what it usually means and what to check first, like a knowledge article for the on-call person.



Built from my own experience in mainframe production support, where the first minutes of a 3 AM failure are spent recognizing the abend code and remembering what to look at. This automates that lookup.



\## How it works



1\. Scans a job log for step results (`IEF142I`) and abend messages (`IEF450I`)

2\. Groups results by job and flags steps with a non-zero condition code

3\. Looks each abend up in `abends.json`, a small knowledge base of common codes

4\. Prints a report with the meaning and the first things to check

5\. Exits with code `1` if any job abended, so it can be used in a script or pipeline



Abends it doesn't recognize are flagged rather than ignored, so the knowledge base can grow over time.



\## Usage



```bash

python analyzer.py sample.log

```



No installs needed, it uses only Python's standard library.



\## Example output



```

JOB PAYJOB01

&#x20; STEP010  OK (RC 0000)

&#x20; STEP015  WARNING (RC 0004)

&#x20; STEP020  ABEND S0C7: Data exception

&#x20;          Meaning: A numeric field contains invalid data, such as spaces or garbage in a packed decimal (COMP-3) field.

&#x20;          Check first:

&#x20;            1. Look at the input file for non-numeric data in numeric fields

&#x20;            2. Find the failing offset in the dump and match it to the compile listing

&#x20;            3. Check for uninitialized working-storage fields



JOB ORDJOB03

&#x20; STEP010  OK (RC 0000)

&#x20; STEP020  ABEND SB37: Out of space (volume)

&#x20;          Meaning: The output dataset ran out of space on the volume.

&#x20;          Check first:

&#x20;            1. Increase the SPACE allocation in the DD statement

&#x20;            2. Check whether the output was much larger than usual



JOB ARCJOB04

&#x20; STEP010  ABEND U4038: not in knowledge base yet

&#x20;          Add it to abends.json



Summary: 4 jobs, 3 abends, 1 warning

```



\## Extending the knowledge base



Add an entry to `abends.json` with a name, a meaning and a list of first checks. The next run picks it up automatically.



\## About the sample data



`sample.log` is entirely made up, with invented job names. No real job output or client data is used anywhere in this project.



\## Future improvements



\- Scan a whole folder of logs in one run

\- Recognize more message types and condition-code rules

\- JSON output for dashboards and alerting

\- Enrich each abend with a link to a runbook or a ServiceNow knowledge article

