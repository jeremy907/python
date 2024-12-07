import os
import subprocess
import requests
import ipaddress

def download_cidr_list(url):
    """
    从指定的URL下载CIDR列表。

    参数:
    url (str): 包含CIDR列表的URL。

    返回:
    list: 包含CIDR格式网段的列表。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.RequestException as e:
        print(f"无法下载CIDR列表：{e}")
        return []

def get_routes():
    """
    获取当前路由表。

    返回:
    list: 包含路由信息的列表。
    """
    try:
        result = subprocess.check_output("route print", shell=True, text=True)
        return result.splitlines()
    except subprocess.SubprocessError as e:
        print(f"获取路由表时出错：{e}")
        return []

def clear_routes_by_gateway(gateway_v4=None, gateway_v6=None):
    """
    清理指定网关的所有路由，但保留 0.0.0.0 和 ::/0 默认路由。

    参数:
    gateway_v4 (str): 要清理的IPv4网关地址。
    gateway_v6 (str): 要清理的IPv6网关地址。
    """
    try:
        # 清理IPv4路由
        if gateway_v4:
            result = subprocess.check_output("ip route show", shell=True, text=True)
            for line in result.splitlines():
                if gateway_v4 in line and not line.startswith("default"):
                    target_route = line.split()[0]
                    os.system(f"ip route del {target_route}")
                    print(f"已删除IPv4路由：{target_route}")

        # 清理IPv6路由
        if gateway_v6:
            result = subprocess.check_output("ip -6 route show", shell=True, text=True)
            for line in result.splitlines():
                if gateway_v6 in line and not line.startswith("default"):
                    target_route = line.split()[0]
                    os.system(f"ip -6 route del {target_route}")
                    print(f"已删除IPv6路由：{target_route}")
    except subprocess.SubprocessError as e:
        print(f"清理路由时出错：{e}")

def update_routes(cidr_list, gateway_v4=None, gateway_v6=None):
    """
    根据CIDR网段列表更新路由。

    参数:
    cidr_list (list): 包含CIDR格式网段的列表。
    gateway_v4 (str): IPv4网关地址。如果为 None，则跳过IPv4路由配置。
    gateway_v6 (str): IPv6网关地址。如果为 None，则跳过IPv6路由配置。
    """
    ipv6_gateway_dev = "ovs_eth1" # IPv6网卡的If值

    for cidr in cidr_list:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            if network.version == 4:  # IPv4
                if gateway_v4:
                    os.system(f"ip route add {network} via {gateway_v4}")
                    print(f"已更新IPv4路由：{network} 通过 {gateway_v4}")
                else:
                    print(f"跳过IPv4路由：{network}（未提供IPv4网关）")
            elif network.version == 6:  # IPv6
                if gateway_v6:
                    os.system(f"ip -6 route add {network} via {gateway_v6} dev {ipv6_gateway_dev}")
                    print(f"已更新IPv6路由：{network} 通过 {gateway_v6} dev {ipv6_gateway_dev}")
                else:
                    print(f"跳过IPv6路由：{network}（未提供IPv6网关）")
        except Exception as e:
            print(f"处理网段 {cidr} 时出错：{e}")

# 内网网段列表
PRIVATE_NETWORKS = [
    "192.168.2.0/24",
    "192.168.78.0/24"
]
    
def main():
    ipv4_gateway = "192.168.78.1"  # 替换为实际的IPv4网关地址
    ipv6_gateway = "fe80::20c:29ff:fe39:33a4"  # 替换为实际的IPv6网关地址

    # 从URL获取IPv4和IPv6地址列表
    ipv4_url = "https://ispip.clang.cn/unicom_cnc_cidr.txt"
    ipv6_url = "https://ispip.clang.cn/unicom_cnc_ipv6.txt"

    ipv4_cidr_list = download_cidr_list(ipv4_url)
    if not ipv4_cidr_list:
        print("IPv4 CIDR列表为空，跳过IPv4路由更新。")

    ipv6_cidr_list = download_cidr_list(ipv6_url)
    if not ipv6_cidr_list:
        print("IPv6 CIDR列表为空，跳过IPv6路由更新。")

    for privateip in PRIVATE_NETWORKS:
        ipv4_cidr_list.append(privateip)
        
    # 清理旧路由
    clear_routes_by_gateway(gateway_v4=ipv4_gateway, gateway_v6=ipv6_gateway)



    # 更新新路由
    if ipv4_cidr_list:
        update_routes(ipv4_cidr_list, gateway_v4=ipv4_gateway)
    if ipv6_cidr_list:
        update_routes(ipv6_cidr_list, gateway_v6=ipv6_gateway)

if __name__ == "__main__":
    main()
