#!/usr/bin/env python3
#Author: Chorder
#Website: https://chorder.net

import os,sys 
import urllib.parse
import urllib.request
import concurrent.futures

def download_ts_file(ts):
    ts_url = ts['ts_url']
    ts_file = ts['ts_file']
    try:
        urllib.request.urlretrieve( ts_url, ts_file)
        return ts_file 
    except:
        return None 

def load_ts_list(url,folder):
    ts_list = []
    _u = urllib.parse.urlparse( url )
    _path = "/".join( _u.path.split("/")[0:-1] )+"/"

    host_with_port = "%s://%s" %  (_u.scheme,_u.netloc)
    host_with_path = "%s://%s%s" % (_u.scheme,_u.netloc,_path)
    
    body = urllib.request.urlopen( url ).read().decode()
    if not body.startswith('#EXTM3U'):
        print("[-] 不是有效的m3u8文件，请检查URL")
        exit()
    ts_index = 0 
    for line in body.split("\n"):
        if line and not line.startswith("#"):
            if line.startswith("/"):
                ts_url = "%s%s" % (host_with_port,line)
            else:
                ts_url = "%s%s" % (host_with_path,line)
            ts_list.append( {
                "ts_index": ts_index,
                "ts_url": ts_url,
                "ts_file": "%s/%s.ts" % (folder,ts_index)
            } )
            ts_index += 1
    return ts_list

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\n* 多线程m3u8下载器\n* Author: Chorder\n* Website: https://chorder.net\n")
        print("Usage:\n\t%s m3u8_url output_folder" % __file__)
        print("Example:\n\t%s http://www.x.com/x.m3u8 output" % __file__)
        exit()
    m3u8_url = sys.argv[1]
    output = sys.argv[2]
    
    if not os.path.exists(output):
        os.makedirs(output)
    ts_list = load_ts_list( m3u8_url,output )
    print("[+] m3u8列表解析完成，共%s个片段" % len(ts_list))

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ts = {executor.submit(download_ts_file, ts): ts for ts in ts_list}
        for future in concurrent.futures.as_completed(future_to_ts):
            ts = future_to_ts[future]
            try:
                ts_file = future.result()
            except Exception as exc:
                sys.stdout.write('\r%r 下载失败: %s' % (ts, exc))
            else:
                sys.stdout.write('\r%r 下载成功, %s K' % (ts['ts_url'],os.path.getsize(ts_file)/1024 ) )
                
    print("\r[+] 下载完成，开始合并ts文件")
    with open( "%s.ts" % output, "wb" ) as f:
       for ts in ts_list:
           sys.stdout.write("\r合并 %s" % ts['ts_file'])
           f.write( open(ts['ts_file'],'rb').read() )
    f.close()
    print("\r[+] 合并完成，保存在 %s.ts" % output )
