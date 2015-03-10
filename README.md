# CheckServiceHealth
This is the check service health service for my FYP. It is written in Python. It uses APScheduler for scheduling.
It is a monitoring tool and is responsible for scheduling checks to make sure services are up and running.

## License

None

## Setting up CheckServiceHealth service on AWS

- Created AWS EC2 Linux instance
- Connected to instance using FileZilla using Public DNS and .pem keyfile
- Uploaded application directory to server
- Connected to server instance using PuTTy using ec2-user@PublicDNS and .ppk keyfile for SSH Auth

## Application Setup Required
- Installed apscheduler -> sudo easy_install apscheduler
- Installed gcc -> sudo yum install gcc-c++
- Installed python3.4.2 -> sudo wget http://www.python.org/ftp/python/3.4.2/Python-3.4.2.tgz
- Instructions - (http://stackoverflow.com/questions/6630873/how-to-download-python-from-command-line)
- Set python default version to new verion (3.4.2) -> alias python=/usr/local/bin/python3.4
- Installed python-dev -> sudo yum install python-devel
- Installed zmq binding -> sudo easy_install pyzmq
- Installed config parser -> sudo easy_install configparser
- Installed enum -> sudo easy_install enum

- Running the service -> sudo python /home/ec2-user/CheckHealthService/main.py

- Service runs and works as expected

