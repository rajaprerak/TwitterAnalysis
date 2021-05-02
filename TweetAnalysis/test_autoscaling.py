import subprocess
import sys
requests = sys.argv[1]
concurrent_requests = sys.argv[2]
subprocess.run(["ab", "-n",requests,"-c",concurrent_requests,"https://certain-torus-307806.wl.r.appspot.com/autoscaling/"])