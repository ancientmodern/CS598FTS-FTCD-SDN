# A Fault-tolerant, Consistent and Distributed SDN Controller (FTCD-SDN)

## Install
1. Install Mininet on node-0
Prerequisite: Python >= 3.6
    ```
    sudo apt update && sudo apt install -y mininet
    ```
2. Install Ryu, pysyncobj and numpy on node-{1,2,3}
Prerequisite: Python >= 3.6, pip >= 23.1.2
    ```
    pip3 install ryu pysyncobj numpy
    ```
3. Install Go on node-{1,2,3}
Requirement: Go >= 1.20
Refer to: https://go.dev/doc/install
4. Clone the repo
    ```
    git clone --recurse-submodules https://github.com/lanzhgx/CS598FTS-FinalProject.git
    # or use ssh
    ```
5. Retrieve all Go module dependencies
    ```
    cd shared_registers
    go mod tidy
    ```

## Run
### 1. Start Data Store on node-{1,2,3}
1. Baseline
    ```
    python3 uds/simple_server.py
    ```
2. or Raft
    ```
    python3 raft/raft_db.py --leader "node-1:9000" --followers "node-2:9000" "node-3:9000" # change args on different nodes
    ```
3. or Shared Registers
    ```
    # First compile
    cd shared_registers
    make

    # Start replica
    ./output/replica

    # Start proxy (open another terminal)
    ./output/proxy -type reg -cid ${cid} # cid normally from 1 to 3
    ```

### 2. Start Controllers on node-{1,2,3}
```
ryu-manager new_controller.py
```

### 3. Start Mininet on node-0
```
mn -c
python3 switch-host-takeover-linear.py
```

### 4. Benchmark!
```
# Inside Mininet
mininet> pingall
mininet> dump
```

Copy all output from dump to benchmark/host_info.txt,

```
# On node-0
cd benchmark
./one_ping_all.sh
```

Wait about 15 seconds, manually terminate one controller using ctrl + C, then wait one_ping_all.sh to finish,

```
cd ..
python3 benchmark/process_ping_logs.py
```

Now you can see the result in `benchmark/latency_data`.
