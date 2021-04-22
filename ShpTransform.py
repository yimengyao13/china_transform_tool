# -*- coding: utf-8 -*-
try:
    from osgeo import gdal
    from osgeo import ogr
    from osgeo import osr
except ImportError:
    import gdal
    import ogr
    import osr
from shutil import copyfile
import os
from .CoordTransform import gcj02tobd09,bd09togcj02,wgs84togcj02,gcj02towgs84,wgs84tomercator,mercatortowgs84,bd09tomercator,mercatortobd09
# 写入shp文件,polygon
# coord_type,code_name, field_list, result_list

def polygon_transform(geom_polygon,coord_original,coord_target):
    geom_type = geom_polygon.GetGeometryType()
    z_value = ogr.GT_HasZ(geom_type)
    # print(z_value)
    geom_col_polygon = ogr.Geometry(ogr.wkbGeometryCollection)
    geom_col_polygon.AddGeometry(geom_polygon)
    geom_poly = geom_polygon
    # print(geom_poly.GetGeometryCount())
    geom_poly_o_count = geom_poly.GetGeometryCount()
    for m in range(0,geom_poly_o_count):
        geom_poly.RemoveGeometry(geom_poly_o_count-m-1)
    # print('geom_poly')
    # print(geom_poly)
    # 获取polygon对象的边界
    boundary_polygon = geom_col_polygon.GetGeometryRef(0).GetBoundary()
    # print('boundary_polygon')
    # print(boundary_polygon)
    # 获取边界的数量，如果大于1，说明有孔洞
    boundary_polygon_count = boundary_polygon.GetGeometryCount()
    # print('boundary_polygon_count')
    # print(boundary_polygon_count)
    if boundary_polygon_count == 0:
        boundary_polygon_point_count = boundary_polygon.GetPointCount()
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for j in range(boundary_polygon_point_count):
            point_polygon = boundary_polygon.GetPoint(j)
            # 坐标系转换
            if coord_original == 'gcj02' and coord_target == 'wgs84':
                point_polygon_trans = gcj02towgs84(point_polygon[0], point_polygon[1])
            elif coord_original == 'wgs84' and coord_target == 'gcj02':
                point_polygon_trans = wgs84togcj02(point_polygon[0], point_polygon[1])
            elif coord_original == 'gcj02' and coord_target == 'bd09':
                point_polygon_trans = gcj02tobd09(point_polygon[0], point_polygon[1])
            elif coord_original == 'bd09' and coord_target == 'gcj02':
                point_polygon_trans = bd09togcj02(point_polygon[0], point_polygon[1])
            elif coord_original == 'wgs84' and coord_target == 'bd09':
                point_polygon_trans_gcj02 = wgs84togcj02(point_polygon[0], point_polygon[1])
                point_polygon_trans = gcj02tobd09(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
            elif coord_original == 'bd09' and coord_target == 'wgs84':
                point_polygon_trans_gcj02 = bd09togcj02(point_polygon[0], point_polygon[1])
                point_polygon_trans = gcj02towgs84(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
            else:
                point_polygon_trans = [point_polygon[0], point_polygon[1]]
            # 添加坐标点
            if z_value == 1:
                ring.AddPoint(point_polygon_trans[0],point_polygon_trans[1],point_polygon[2])
            else:
                ring.AddPoint_2D(point_polygon_trans[0],point_polygon_trans[1])
        geom_poly.AddGeometry(ring)
    else:
        for i in range(boundary_polygon_count):
            boundary_polygon_ring = boundary_polygon.GetGeometryRef(i)
            boundary_polygon_ring_point_count = boundary_polygon_ring.GetPointCount()
            ring = ogr.Geometry(ogr.wkbLinearRing)
            for j in range(0,boundary_polygon_ring_point_count):
                point_polygon = boundary_polygon_ring.GetPoint(j)
                # print('point_polygon')
                # print(point_polygon)
                # 坐标系转换
                if coord_original == 'gcj02' and coord_target == 'wgs84':
                    point_polygon_trans = gcj02towgs84(point_polygon[0], point_polygon[1])
                elif coord_original == 'wgs84' and coord_target == 'gcj02':
                    point_polygon_trans = wgs84togcj02(point_polygon[0], point_polygon[1])
                elif coord_original == 'gcj02' and coord_target == 'bd09':
                    point_polygon_trans = gcj02tobd09(point_polygon[0], point_polygon[1])
                elif coord_original == 'bd09' and coord_target == 'gcj02':
                    point_polygon_trans = bd09togcj02(point_polygon[0], point_polygon[1])
                elif coord_original == 'wgs84' and coord_target == 'bd09':
                    point_polygon_trans_gcj02 = wgs84togcj02(point_polygon[0], point_polygon[1])
                    point_polygon_trans = gcj02tobd09(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
                elif coord_original == 'bd09' and coord_target == 'wgs84':
                    point_polygon_trans_gcj02 = bd09togcj02(point_polygon[0], point_polygon[1])
                    point_polygon_trans = gcj02towgs84(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
                else:
                    point_polygon_trans = [point_polygon[0], point_polygon[1]]
                # 添加坐标点
                if z_value == 1:
                    ring.AddPoint(point_polygon_trans[0], point_polygon_trans[1], point_polygon[2])
                else:
                    ring.AddPoint_2D(point_polygon_trans[0], point_polygon_trans[1])
            geom_poly.AddGeometry(ring)
    return geom_poly

def multi_polygon_transform(geom_polygon,coord_original,coord_target):
    geom_col = ogr.Geometry(ogr.wkbGeometryCollection)
    for g in geom_polygon:
        geom_col.AddGeometry(g)
    geom_polygon_count = geom_polygon.GetGeometryCount()
    for m in range(0,geom_polygon_count):
        geom_polygon.RemoveGeometry(geom_polygon_count-m-1)
    for g in geom_col:
        g_trans = polygon_transform(g,coord_original,coord_target)
        geom_polygon.AddGeometry(g_trans)
    return geom_polygon
def polyline_transform(geom_polyline,coord_original,coord_target):
    geom_type = geom_polyline.GetGeometryType()
    z_value = ogr.GT_HasZ(geom_type)
    # print(z_value)
    geom_polyline_count = geom_polyline.GetPointCount()
    for i in range(0,geom_polyline_count):
        point_orginal = geom_polyline.GetPoint(i)
        # 坐标系转换
        if coord_original == 'gcj02' and coord_target == 'wgs84':
            point_polygon_trans = gcj02towgs84(point_orginal[0], point_orginal[1])
        elif coord_original == 'wgs84' and coord_target == 'gcj02':
            point_polygon_trans = wgs84togcj02(point_orginal[0], point_orginal[1])
        elif coord_original == 'gcj02' and coord_target == 'bd09':
            point_polygon_trans = gcj02tobd09(point_orginal[0], point_orginal[1])
        elif coord_original == 'bd09' and coord_target == 'gcj02':
            point_polygon_trans = bd09togcj02(point_orginal[0], point_orginal[1])
        elif coord_original == 'wgs84' and coord_target == 'bd09':
            point_polygon_trans_gcj02 = wgs84togcj02(point_orginal[0], point_orginal[1])
            point_polygon_trans = gcj02tobd09(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
        elif coord_original == 'bd09' and coord_target == 'wgs84':
            point_polygon_trans_gcj02 = bd09togcj02(point_orginal[0], point_orginal[1])
            point_polygon_trans = gcj02towgs84(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
        else:
            point_polygon_trans = [point_orginal[0], point_orginal[1]]
        if z_value == 1:
            geom_polyline.SetPoint(i,point_polygon_trans[0],point_polygon_trans[1],point_orginal[2])
        else:
            geom_polyline.SetPoint_2D(i,point_polygon_trans[0],point_polygon_trans[1])
    return geom_polyline
def multi_polyline_transform(geom_polyline,coord_original,coord_target):
    geom_col = ogr.Geometry(ogr.wkbGeometryCollection)
    for g in geom_polyline:
        geom_col.AddGeometry(g)
    geom_polyline_count = geom_polyline.GetGeometryCount()
    for m in range(0,geom_polyline_count):
        geom_polyline.RemoveGeometry(geom_polyline_count-m-1)
    for g in geom_col:
        g_trans = polyline_transform(g,coord_original,coord_target)
        geom_polyline.AddGeometry(g_trans)
    return geom_polyline
def point_transform(geom_point,coord_original,coord_target):
    geom_type = geom_point.GetGeometryType()
    z_value = ogr.GT_HasZ(geom_type)
    # print(z_value)
    # 坐标系转换
    if coord_original == 'gcj02' and coord_target == 'wgs84':
        point_polygon_trans = gcj02towgs84(geom_point.GetX(), geom_point.GetY())
    elif coord_original == 'wgs84' and coord_target == 'gcj02':
        point_polygon_trans = wgs84togcj02(geom_point.GetX(), geom_point.GetY())
    elif coord_original == 'gcj02' and coord_target == 'bd09':
        point_polygon_trans = gcj02tobd09(geom_point.GetX(), geom_point.GetY())
    elif coord_original == 'bd09' and coord_target == 'gcj02':
        point_polygon_trans = bd09togcj02(geom_point.GetX(), geom_point.GetY())
    elif coord_original == 'wgs84' and coord_target == 'bd09':
        point_polygon_trans_gcj02 = wgs84togcj02(geom_point.GetX(), geom_point.GetY())
        point_polygon_trans = gcj02tobd09(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
    elif coord_original == 'bd09' and coord_target == 'wgs84':
        point_polygon_trans_gcj02 = bd09togcj02(geom_point.GetX(), geom_point.GetY())
        point_polygon_trans = gcj02towgs84(point_polygon_trans_gcj02[0], point_polygon_trans_gcj02[1])
    else:
        point_polygon_trans = [geom_point.GetX(), geom_point.GetY()]
    if z_value == 1:
        geom_point.SetPoint(0,point_polygon_trans[0],point_polygon_trans[1], geom_point.GetZ())
    else:
        geom_point.SetPoint_2D(0,point_polygon_trans[0],point_polygon_trans[1])
    return geom_point
def multi_point_transform(geom_point,coord_original,coord_target):
    # print(geom_point)
    geom_col = ogr.Geometry(ogr.wkbGeometryCollection)
    for g in geom_point:
        geom_col.AddGeometry(g)
    geom_point_count = geom_point.GetGeometryCount()
    for m in range(0,geom_point_count):
        geom_point.RemoveGeometry(geom_point_count-m-1)
    for g in geom_col:
        g_trans = point_transform(g,coord_original,coord_target)
        geom_point.AddGeometry(g_trans)
    # print(geom_point)
    return geom_point
def transform_shpfile(read_path_str,write_path_str,coord_original,coord_target):
    write_file_name = write_path_str.split('.')[0]
    read_file_name = read_path_str.split('.')[0]
    if os.path.exists(read_file_name+'.cpg'):
        copyfile(read_file_name+'.cpg',write_file_name+'.cpg')
    if os.path.exists(read_file_name+'.dbf'):
        copyfile(read_file_name+'.dbf',write_file_name+'.dbf')
    if os.path.exists(read_file_name+'.prj'):
        copyfile(read_file_name+'.prj',write_file_name+'.prj')
    if os.path.exists(read_file_name+'.qpj'):
        copyfile(read_file_name+'.qpj',write_file_name+'.qpj')
    if os.path.exists(read_file_name+'.shp'):
        copyfile(read_file_name+'.shp',write_file_name+'.shp')
    if os.path.exists(read_file_name+'.shx'):
        copyfile(read_file_name+'.shx',write_file_name+'.shx')
    # 支持中文路径
    gdal.SetConfigOption('GDAL_FILENAME_IS_UTF8', 'YES')
    fcode = open(write_file_name+'.cpg','r')
    fcodelines = fcode.readlines()
    code_name = fcodelines[0].strip('\n')
    fcode.close()
    # 支持中文编码
    gdal.SetConfigOption('SHAPE_ENCODING', code_name)
    # 注册所有的驱动
    ogr.RegisterAll()
    # 打开数据
    ds = ogr.Open(write_file_name+'.shp', 1)
    if ds == None:
        print('打开文件失败！')
    # 获取数据源中的图层个数，shp数据图层只有一个，gdb、dxf会有多个
    iLayerCount = ds.GetLayerCount()
    print('图层个数 = ', iLayerCount)
    # 获取第一个图层
    oLayer = ds.GetLayerByIndex(0)
    if oLayer == None:
        print('获取图层失败！')
    # 对图层进行初始化
    oLayer.ResetReading()
    # 输出图层中的要素个数
    num = oLayer.GetFeatureCount(0)
    oFid = oLayer.GetFIDColumn()
    print(oFid)
    oDefn = oLayer.GetLayerDefn()
    # 获取要素
    for i in range(0, num):
        ofeature = oLayer.GetFeature(i)
        oLayer.DeleteFeature(i)
        geom = ofeature.GetGeometryRef()
        geom_type = geom.GetGeometryName()
        # print(geom_type)
        if 'MULTIPOLYGON' in geom_type:
            ofeature.SetGeometry(multi_polygon_transform(geom, coord_original, coord_target))
        elif 'MULTILINESTRING' in geom_type:
            ofeature.SetGeometry(multi_polyline_transform(geom, coord_original, coord_target))
        elif 'MULTIPOINT' in geom_type:
            ofeature.SetGeometry(multi_point_transform(geom, coord_original, coord_target))
        elif 'POLYGON' in geom_type and 'MULTI' not in geom_type:
            ofeature.SetGeometry(polygon_transform(geom, coord_original, coord_target))
        elif 'LINESTRING' in geom_type and 'MULTI' not in geom_type:
            ofeature.SetGeometry(polyline_transform(geom, coord_original, coord_target))
        elif 'POINT' in geom_type and 'MULTI' not in geom_type:
            ofeature.SetGeometry(point_transform(geom, coord_original, coord_target))
        oLayer.CreateFeature(ofeature)
    ds.Destroy()
    del ds

