import numpy as np
from itertools import combinations
from scipy.spatial import ConvexHull
from scipy.spatial import Delaunay
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pymatgen.core import Structure
import math
import os
from typing import List, Tuple, Any, Dict, Union
import logging
import pandas as pd
from utils import _add_error_xml, _add_info_xml, _read_parameters

logging.basicConfig(level=logging.INFO, handlers=None)


def create_logger():
    log = logging.getLogger(name="CystalShell_logger")
    console = logging.StreamHandler()
    fmt = logging.Formatter(
        fmt=
        "%(asctime)s - [%(funcName)s-->line:%(lineno)d] - %(levelname)s:%(message)s"
    )
    console.setFormatter(fmt=fmt)
    # log.handlers = None
    log.addHandler(console)
    log.propagate = False
    return log


class CrystalShell():

    def __init__(self, filename: str):
        """晶体壳层分析工具，输入若干个cif文件，找出若干壳层信息，并以图片和坐标的形式返回。
        
        Args:
            filename (str): 一个cif文件名。
        """
        self.filename = filename
        self.pos_abc: Dict = {}  #归一化后的比例
        self.pos_xyz: Dict = {}  #真实的原子坐标
        self.atoms: Dict = {}  #原子
        self.center: int = None  #中心原子index
        self.info: Dict = {}  #晶胞信息
        self.log = create_logger()
        self.read_cif()
        # print(self.info)
        self._cal_hist()
        self._get_mid_gaps()
        self.find_convex()

    def read_cif(self):
        """读取cif文件。
        """
        assert os.path.isfile(self.filename), '文件或路径不存在'
        stru = Structure.from_file(self.filename)  #从文件中读出坐标
        self.info = stru.as_dict()
        for i, sp in enumerate(stru.sites):
            self.atoms.setdefault(i, str(sp.specie.symbol))
            self.pos_abc.setdefault(i, [sp.a, sp.b, sp.c])
            self.pos_xyz.setdefault(i, [sp.x, sp.y, sp.z])
            # print('读取到cif文件{}的构成为:{}'.format(self.filename, stru.formula))
        self.log.info(msg='读取到cif文件{}的构成为:{}'.format(self.filename,
                                                     stru.formula),
                      stack_info=0)
        self.pos_matrix = np.array(list(self.pos_xyz.values()))
        self.center = self._cal_center()

    def _cal_center(self):
        """计算中心原子

        Returns:
            int:中心原子的索引。
        """
        center_vec = np.array([
            self.info['lattice']['a'] / 2, self.info['lattice']['b'] / 2,
            self.info['lattice']['c'] / 2
        ])
        dis = np.linalg.norm(center_vec - self.pos_matrix, axis=1)
        return np.argmin(dis)

    def _cal_hist(self):
        """计算距离直方图
        
        Returns:
              None
        """
        self.dis = {}
        # print(f'center:{self.center}')
        for i in range(self.pos_matrix.shape[0]):
            if i != self.center:
                vec = self.pos_matrix[i] - self.pos_matrix[self.center]
                dis = np.around(np.linalg.norm(vec), 6)
                self.dis[i] = dis
        distances = list(self.dis.values())
        distances /= min(distances)
        # self._draw_hist(distances)

    def _draw_hist(self, distances):
        """绘制距离直方图

        Args:
            distances (List): 距离列表
        """
        plt.hist(x=distances,
                 bins=30,
                 range=(1, math.ceil(max(distances))),
                 cumulative=False,
                 rwidth=0.5,
                 histtype='barstacked')
        plt.xlabel('d/dmin')
        plt.ylabel('n')
        # plt.show()

    def _get_mid_gaps(self):
        """找到所有的中间gap。
        """
        unique_d = list(set(self.dis.values()))
        self.mid_gaps = []
        for i in range(len(unique_d) - 1):
            self.mid_gaps.append(round(sum(unique_d[i:i + 2]) / 2, 6))
        self.mid_gaps.append(unique_d[-1] + 1)

    def _get_convex(self, pos):
        """找到凸包壳层。

        Args:
            pos (NDArray): 点的坐标

        Returns:
            None | hull: 一个凸包或无。
        """
        hull = ConvexHull(pos)
        if len(hull.vertices) != pos.shape[0]:
            return None
        else:
            if self.check_inner(hull, pos,
                                center=self.pos_matrix[self.center]):
                return hull
            else:
                return None

    def draw(self, hull, idx, remain_idx, c, saveas='./'):
        """绘制壳层示意图

        Args:
            hull (_type_): 壳层凸包
            idx (_type_): 壳层原子的索引
            remain_idx (_type_): 非壳层原子的索引
            c (_type_): 颜色
            saveas (str, optional): 存储路径. Defaults to './'.
        """
        pos = self.pos_matrix[idx]
        remain_convex = self.pos_matrix[remain_idx]
        fig = plt.figure()
        ax = Axes3D(fig, auto_add_to_figure=False)
        fig.add_axes(ax)
        convex = pos[hull.vertices, :]
        ax.set_title('3d_convex_hull')  # 设置本图名称
        ax.scatter(convex[:, 0],
                   convex[:, 1],
                   convex[:, 2],
                   c='k',
                   cmap='grays')  # 绘制数据点 c: 'r'红色，'y'黄色，等颜色
        ax.scatter(remain_convex[:, 0],
                   remain_convex[:, 1],
                   remain_convex[:, 2],
                   c='b',
                   cmap='grays')  # 绘制数据点 c: 'r'红色，'y'黄色，等颜色
        ax.set_xlabel('X')  # 设置x坐标轴
        ax.set_ylabel('Y')  # 设置y坐标轴
        ax.set_zlabel('Z')  # 设置z坐标轴
        for i in range(len(remain_idx)):
            ax.text(remain_convex[i, 0], remain_convex[i, 1],
                    remain_convex[i, 2], self.atoms[int(remain_idx[i])])
        for i in range(len(idx)):
            ax.text(remain_convex[i, 0], remain_convex[i, 1],
                    remain_convex[i, 2], self.atoms[int(idx[i])])
        lines = set()
        for simple in hull.simplices:
            for src, dst in combinations(simple, 2):
                lines |= {(src, dst)}
        for line in lines:
            ax.plot3D(pos[line, 0], pos[line, 1], pos[line, 2], c=c)
        plt.savefig(saveas)
        # plt.show()
        plt.pause(1)
        plt.close()

    def check_inner(self, hull, pos, center=[0.5, 0.5, 0.5]):
        """检查中心原子是否在壳层内部。

        Args:
            hull (_type_): 壳层凸包
            pos (_type_): 点的坐标
            center (list, optional): 中心原子坐标. Defaults to [0.5, 0.5, 0.5].

        Returns:
            Boolean:True | False
        """
        v = 0.0
        for pointidxs in hull.simplices:
            points = pos[pointidxs]
            ab = points[1] - points[0]
            ac = points[2] - points[0]
            ap = center - points[0]
            v += np.abs(np.dot(ap, np.cross(ab, ac)) / 6)  #提及相加相等也可以或说明点在内部
        if np.allclose([v], [hull.volume]):
            return True
        else:
            return False

    def find_convex(self):
        """根据cif文件找壳层信息。
        """
        colormap = [
            'r', 'orange', 'y', 'g', 'b', 'm', 'c', 'darkgrey', 'grey',
            'dimgrey', 'black'
        ]
        self.shell_and_pics = []
        i = 1
        for gap in self.mid_gaps:
            idx = []
            for k, v in self.dis.items():
                if v < gap:
                    idx.append(k)
            if idx == [] or len(idx) < 4:
                continue
            hull = self._get_convex(self.pos_matrix[idx, :])

            if hull:
                for id in idx:
                    del self.dis[id]
                remain_idx = np.setdiff1d(
                    np.array(range(self.pos_matrix.shape[0])), np.array(idx))
                self.draw(hull, idx, remain_idx, colormap.pop(0),
                          f'./第{i}壳层示意图.jpg')
                shell = pd.DataFrame(np.around(self.pos_matrix[idx, :], 4),
                                     columns=['x', 'y', 'z'], index=False)
                shell.insert(0, 'atom', [self.atoms[k] for k in idx])
                self.shell_and_pics.append((f'./第{i}壳层示意图.jpg', shell))
                self.log.info(msg=f'找到第{i}壳层,正在保存')
                i += 1


def main():
    try:
        parameters = _read_parameters()
        inputCSV = parameters["inputCSV"]
    except Exception as e:
        _add_error_xml("Parameters Error", str(e))
        with open('log.txt', 'a') as fp:
            fp.write('error\n')
        return

    try:
        c = CrystalShell(filename=inputCSV)
    except Exception as e:
        _add_error_xml("Convex CIF File Error", str(e))
        with open('log.txt', 'a') as fp:
            fp.write('error\n')
        return 
    
    try:
        _add_info_xml(c.shell_and_pics)
    except Exception as e:
        _add_error_xml("XML Error", str(e))
        with open('log.txt', 'a') as fp:
            fp.write('error\n')
    
    with open('log.txt', 'a') as fp:
        fp.write('finish\n')
    

if __name__ == "__main__":
    import sys
    console = sys.stdout
    file = open("task_log.txt", "w")
    sys.stdout = file
    main()
    sys.stdout = console
    file.close
