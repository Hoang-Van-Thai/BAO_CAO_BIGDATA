from flask import Flask, request, render_template, jsonify
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel

app = Flask(__name__)

# Khởi tạo SparkContext
spark = SparkSession.builder \
    .appName("MovieRecommendationSystem") \
    .config("spark.driver.memory", "8g") \
    .config("spark.shuffle.spill.numElementsForceSpillThreshold", 50000) \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "1g") \
    .config("spark.executorEnv.OPENBLAS_NUM_THREADS", "1") \
    .getOrCreate()

# Load mô hình ALS từ HDFS
model_path = "hdfs://localhost:9000/Models/modelASL"
als_model = ALSModel.load(model_path)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Nhận dữ liệu đầu vào từ biểu mẫu
        user_id = int(request.form['user_id'])

        # Thực hiện dự đoán bằng mô hình ALS
        recommendations = als_model.recommendForUserSubset(spark.createDataFrame([(user_id,)], ['userId']), 10)
        movie_ids = [r.movieId for r in recommendations.first().recommendations]

        # Hiển thị user_id và movie_ids đề xuất
        return render_template('recommendations.html', user_id=user_id, movie_ids=movie_ids)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
