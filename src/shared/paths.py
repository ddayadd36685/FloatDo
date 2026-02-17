import os
import sys

def get_base_path():
    """
    获取项目的基础路径，兼容源码运行和编译后的运行
    """
    # Nuitka 打包后，sys.argv[0] 通常是可执行文件的路径
    # 或者检查是否定义了 __compiled__ 属性
    if hasattr(sys, "frozen") or hasattr(sys, "importers") or hasattr(sys, "__compiled__"):
        # 如果是打包后的环境，基准路径通常是可执行文件所在目录
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        # 开发环境，基准路径是当前文件所在目录的上级目录 (假设 paths.py 在 src/shared/ 下)
        # src/shared -> src -> root
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_asset_path(*paths):
    """
    获取资源文件的绝对路径
    """
    return os.path.join(get_base_path(), 'assets', *paths)

def get_data_path(*paths):
    """
    获取数据文件的绝对路径
    """
    return os.path.join(get_base_path(), 'data', *paths)
