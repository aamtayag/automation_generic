#!/opt/anaconda3/bin/python3

# ########################################################
# Script name: firewall_log_generator.py
# Description:
#   Generate realistic-looking firewall syslog entries (INFO/WARNING/ERROR) for testing, analytics, or demos.
# Usage:
#   python3 firewall_log_generator.py --count 500 --out ./firewall_sample.log --seed 42
#   python3 /path/to/firewall_log_generator.py --count 500 --out ./firewall_sample.log
#   python3 /path/to/firewall_log_generator.py --count 1000 --out /tmp/fw.log --seed 123 --burstiness 0.3
# Options:
#   --count N        Number of log entries to generate (default 500)
#   --out PATH       Output file path (default ./firewall_sample.log)
#   --rate R         Approx average messages per second when simulating real-time (optional)
#   --start 'ISO'    Start timestamp in ISO format. Defaults to now.
#   --seed S         Random seed for reproducibility.
#   --burstiness B   Burstiness factor (0.0 - 1.0) to cluster warnings/errors (default 0.2)
# ########################################################


import argparse
import random
import ipaddress
import uuid
import sys
from datetime import datetime, timedelta

SEVERITY = [
    ("INFO", 0.70),
    ("NOTICE", 0.10),
    ("WARNING", 0.12),
    ("ERROR", 0.06),
    ("CRITICAL", 0.02),
]

ACTIONS = ["ACCEPT", "DROP", "REJECT"]
PROTOCOLS = ["TCP", "UDP", "ICMP", "GRE", "ESP"]
INTERFACES = ["eth0", "eth1", "wan0", "lan0", "dmz0"]

REASONS_INFO = [
    "Connection established", "Connection closed", "NAT translation success",
    "Policy matched", "Session aged out", "Health check passed"
]
REASONS_WARN = [
    "Suspicious connection rate", "Unexpected packet", "Possible policy mismatch",
    "Malformed packet", "IP spoofing suspected"
]
REASONS_ERROR = [
    "Policy violation", "Intrusion detected", "Configuration error", "Resource exhausted",
    "Authentication failure", "Firewall rule conflict"
]


def weighted_choice(choices):
    r = random.random()
    upto = 0.0
    for k, w in choices:
        if upto + w >= r:
            return k
        upto += w
    return choices[-1][0]


def random_ipv4(private_bias=0.6):
    if random.random() < private_bias:
        nets = ["10.0.0.0/8", "192.168.0.0/16", "172.16.0.0/12"]
        net = ipaddress.ip_network(random.choice(nets))
        addr = ipaddress.IPv4Address(
            int(net.network_address) + random.randint(1, net.num_addresses - 2)
        )
        return str(addr)
    else:
        while True:
            a = random.randint(1, 254)
            b = random.randint(0, 254)
            c = random.randint(0, 254)
            d = random.randint(1, 254)
            if not (a == 10 or (a == 192 and b == 168) or (a == 172 and 16 <= b <= 31)):
                return f"{a}.{b}.{c}.{d}"


def format_syslog_ts(ts):
    return ts.strftime("%b %d %H:%M:%S")


def make_log_line(ts, host, pid):
    """Return a single-line log entry (no embedded newlines)."""
    sev = weighted_choice(SEVERITY)
    proto = random.choice(PROTOCOLS)
    s_ip = random_ipv4()
    d_ip = random_ipv4(private_bias=0.3)
    s_pt = random.randint(1, 65535) if proto in ["TCP", "UDP"] else 0
    d_pt = random.choice([22, 80, 443, 53, 8080, 3389, 5000, 514, 3306, 1433]) \
        if proto in ["TCP", "UDP"] else 0
    in_if = random.choice(INTERFACES)
    out_if = random.choice(INTERFACES)
    action = random.choices(ACTIONS, weights=[0.6, 0.3, 0.1])[0]
    bytes_cnt = random.randint(0, 15000)
    pkts = max(1, int(bytes_cnt / random.randint(60, 120))) if bytes_cnt > 0 else random.randint(0, 4)
    rule = random.randint(100, 3999)
    uid = uuid.uuid4().hex[:8]

    if sev in ("INFO", "NOTICE"):
        reason = random.choice(REASONS_INFO)
    elif sev == "WARNING":
        reason = random.choice(REASONS_WARN)
    else:
        reason = random.choice(REASONS_ERROR)

    message = (
        f"%FW-{sev}-*.{rule}: {reason}; src={s_ip} dst={d_ip} proto={proto} "
        f"spt={s_pt} dpt={d_pt} action={action} bytes={bytes_cnt} pkts={pkts} "
        f"rule={rule} in={in_if} out={out_if} uid={uid}"
    )

    # Sanitize any stray newline/control characters
    safe_message = "".join(ch for ch in message if ch not in "\r\n\t\x0b\x0c")
    return f"{format_syslog_ts(ts)} {host} firewall[{pid}]: {safe_message}"


def generate_logs(count=500, start_time=None, out_path="firewall_sample.log", seed=None):
    random.seed(seed)
    ts = start_time or datetime.now()
    host = "fw01.corp.example.com"
    pid = random.randint(1000, 9999)

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        for _ in range(count):
            ts += timedelta(seconds=random.expovariate(1 / 1.2))
            line = make_log_line(ts, host, pid)
            f.write(line.rstrip() + "\n")

    print(f"Wrote {count} log lines to: {out_path}")
    return out_path


def parse_args():
    p = argparse.ArgumentParser(description="Generate firewall-style syslog logs.")
    p.add_argument("--count", type=int, default=500, help="Number of log lines to generate")
    p.add_argument("--out", type=str, default="./firewall_sample.log", help="Output file path")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")
    return p.parse_args()


# ###############################
# MAIN
# ###############################

def main():
    args = parse_args()
    generate_logs(count=args.count, out_path=args.out, seed=args.seed)


if __name__ == "__main__":
    main()
