from flask import Flask, jsonify, Blueprint
import pymysql
from datetime import datetime

from config.config import DB_CONFIG


# 创建Blueprint
getProjectDetails_bp = Blueprint("getProjectDetails", __name__)

# 连接数据库
connection = pymysql.connect(**DB_CONFIG)

@getProjectDetails_bp.route("/getProjectDetails/<int:id>", methods=["GET"])
def fetch_project(id):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # 执行SQL查询获取项目信息
            project_sql = "SELECT * FROM project WHERE id = %s"
            cursor.execute(project_sql, (id,))
            result = cursor.fetchone()

            # 如果项目存在
            if result:
                # 执行SQL查询获取担保人信息
                surety_sql = "SELECT name, id_card, phone FROM surety WHERE id = %s"
                cursor.execute(surety_sql, (result['surety_id'],))
                surety_result = cursor.fetchone()

                # 如果担保人存在
                if surety_result:
                    # 将担保人信息添加到项目信息中
                    result['surety_info'] = {
                        'name': surety_result['name'],
                        'phone': surety_result['phone'],
                        'id_card': surety_result['id_card']
                    }

                # 处理项目信息中的其他字段
                result['label'] = result['label'].split(',')
                result['target_amount'] = float(result['target_amount'])
                result['current_amount'] = float(result['current_amount'])
                result['patient_gender'] = '男' if result['patient_gender'] == 'male' else '女'
                result['create_time'] = result['create_time'].strftime('%Y-%m-%d')
                result['deadline'] = result['deadline'].strftime('%Y-%m-%d')

                # 计算年龄
                today = datetime.now().date()
                birth_date = result['patient_birth']
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                result['patient_birth'] = age

                return jsonify(result)
            else:
                return jsonify({"message": "项目未找到"}), 404
    finally:
        connection.close()
        # pass

