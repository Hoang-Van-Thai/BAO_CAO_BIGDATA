# import requests
# from bs4 import BeautifulSoup
#
# # Gửi yêu cầu GET đến trang web
# response = requests.get('https://www.imdb.com/search/title/?groups=top_100&start=51&ref_=adv_nxt')
#
# # Kiểm tra xem yêu cầu đã thành công không
# if response.status_code == 200:
#     # Sử dụng BeautifulSoup để phân tích cú pháp HTML của trang web
#     soup = BeautifulSoup(response.content, 'html.parser')
#
#     # Tạo hoặc mở một tệp văn bản để ghi thông tin
#     with open('phim_top_100_imdb.txt', 'w', encoding='utf-8') as file:
#         # Tìm tất cả các phần tử có class là 'lister-item mode-advanced'
#         movies = soup.find_all('div', class_='lister-item mode-advanced')
#
#         # Lặp qua từng phim và trích xuất thông tin cần thiết
#         for movie in movies:
#             # Trích xuất tiêu đề phim
#             title = movie.h3.a.text.strip() if movie.h3.a else "N/A"
#
#             # Trích xuất năm sản xuất
#             year = movie.h3.find('span', class_='lister-item-year').text.strip() if movie.h3.find('span',
#                                                                                                   class_='lister-item-year') else "N/A"
#
#             # Trích xuất thể loại phim
#             genre = movie.p.find('span', class_='genre').text.strip() if movie.p.find('span', class_='genre') else "N/A"
#
#             # Trích xuất điểm đánh giá từ IMDb
#             rating = movie.find('div', class_='ratings-imdb-rating').strong.text.strip() if movie.find('div',
#                                                                                                        class_='ratings-imdb-rating') else "N/A"
#
#             # Trích xuất thông tin thời lượng từ thẻ <span class="runtime">
#             runtime_span = movie.p.find('span', class_='runtime')
#             runtime = runtime_span.text.strip() if runtime_span else "N/A"
#
#             # Trích xuất giá trị "Votes"
#             votes_tag = movie.find('span', string='Votes:')
#             votes = votes_tag.find_next('span', {'name': 'nv', 'data-value': True}).text.strip() if votes_tag else "N/A"
#
#             # Trích xuất giá trị "Gross"
#             gross_tag = movie.find('span', string='Gross:')
#             gross = gross_tag.find_next('span', {'name': 'nv', 'data-value': True}).text.strip() if gross_tag else "N/A"
#
#             # Viết thông tin của phim vào tệp văn bản
#             file.write(f'Tiêu đề: {title}\n')
#             file.write(f'Năm sản xuất: {year}\n')
#             file.write(f'Thể loại: {genre}\n')
#             file.write(f'Điểm đánh giá: {rating}\n')
#             file.write(f'Thời lượng: {runtime}\n')
#             file.write(f'Votes: {votes}\n')
#             file.write(f'Gross: {gross}\n')
#             file.write('---\n')
#
#     print('Thông tin các phim đã được lưu vào tệp phim_top_100_imdb.txt.')
# else:
#     print('Không thể kết nối đến trang web.')
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import unix_timestamp
# from pyspark.sql.types import TimestampType
# from pyspark.sql.types import StringType
# spark = SparkSession.builder.appName("MergeAndConvert").getOrCreate()
#
#
# # Đọc dữ liệu từ tệp ratings.csv
# ratings_data = spark.read.csv("D:/datamovies/4_2015/ratings.csv", header=True, inferSchema=True)
#
#
# # Đọc dữ liệu từ tệp movies.csv
# movies_data = spark.read.csv("D:/datamovies/4_2015/movies.csv", header=True, inferSchema=True)
#
#
# # Đọc dữ liệu từ tệp tags.csv
# tags_data = spark.read.csv("D:/datamovies/4_2015/tags.csv", header=True, inferSchema=True)
# tags_data = tags_data.withColumn("timestamp", tags_data["timestamp"].cast(StringType()))
#
#
# # Chuyển đổi cột timestamp trong tags_data thành định dạng thời gian đọc được
# tags_data = tags_data.withColumn("timestamp", unix_timestamp("timestamp").cast(TimestampType()))
#
#
# # Gộp dữ liệu từ ratings_data và movies_data dựa trên cột 'movieId'
# merged_data = ratings_data.join(movies_data, on='movieId', how='inner')
#
#
# # Cấu hình Spark để hiển thị đầy đủ nội dung của cột 'title'
# spark.conf.set("spark.sql.repl.eagerEval.enabled", True)
# spark.conf.set("spark.sql.repl.eagerEval.maxNumRows", 20)
#
#
# from pyspark.sql.types import TimestampType
#
#
# # Chuyển đổi cột "timestamp" thành loại dữ liệu thời gian
# merged_data = merged_data.withColumn("timestamp", merged_data["timestamp"].cast(TimestampType()))
# merged_data.show(50, truncate=False)
# #lưu vào ổ cứng\
# merged_data.write.csv("D:/datamovies/4_2015/merged_data_csv")








from pyspark.sql import SparkSession
from pyspark.sql.connect.functions import lit
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, StringType, TimestampType
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
# Khởi tạo SparkSession
spark = SparkSession.builder \
    .appName("MovieRecommendationSystem") \
    .config("spark.driver.memory", "8g") \
    .config("spark.shuffle.spill.numElementsForceSpillThreshold", 50000) \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "1g") \
    .config("spark.executorEnv.OPENBLAS_NUM_THREADS", "1") \
    .getOrCreate()





# Định nghĩa schema cho dữ liệu
schema = StructType([
    StructField("movieId", IntegerType(), True),
    StructField("userId", IntegerType(), True),
    StructField("rating", DoubleType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("title", StringType(), True),
    StructField("genres", StringType(), True)
])

# Đọc dữ liệu với schema đã định nghĩa
csv_data = spark.read.csv("D:/datamovies/merged_data.csv/part-00000-d9263bbf-9b3e-4130-b609-813cf4b5bdde-c000.csv", header=False, schema=schema)



# Hiển thị dữ liệu
csv_data.show()
from pyspark.sql.functions import countDistinct, count, max, min

# Tính tổng số người dùng
total_users = csv_data.select(countDistinct("userId")).first()[0]

# Tính tổng số bộ phim
total_movies = csv_data.select(countDistinct("movieId")).first()[0]

# Tính rating cao nhất
max_rating = csv_data.select(max("rating")).first()[0]

# Tính rating thấp nhất
min_rating = csv_data.select(min("rating")).first()[0]

print(f"Tổng số người dùng: {total_users}")
print(f"Tổng số bộ phim: {total_movies}")
print(f"Rating cao nhất: {max_rating}")
print(f"Rating thấp nhất: {min_rating}")

#biểu đồ cho dữ liệu rating
import matplotlib.pyplot as plt

# Tính tỷ lệ rating trung bình cho mỗi bộ phim
average_ratings = csv_data.groupBy("movieId").agg({"rating": "mean"}).withColumnRenamed("avg(rating)", "average_rating")

# Chuyển đổi dữ liệu thành Pandas DataFrame để vẽ biểu đồ
pd_ratings = average_ratings.toPandas()

# Vẽ biểu đồ
plt.figure(figsize=(12, 6))
plt.hist(pd_ratings["average_rating"], bins=30, edgecolor='black')
plt.xlabel('Điểm Trung Bình')
plt.ylabel('Số Lượng Phim')
plt.title('Phân Phối Điểm Trung Bình Của Các Phim')
plt.show()



# Chia dữ liệu thành tập huấn luyện và tập kiểm tra (80-20)
(training_data, test_data) = csv_data.randomSplit([0.8, 0.2], seed=1234)

# Xây dựng mô hình ALS sử dụng tập huấn luyện
als = ALS(maxIter=15, regParam=0.1, rank=15, userCol="userId", itemCol="movieId", ratingCol="rating", coldStartStrategy="drop", nonnegative=True)
model = als.fit(training_data)

# Đánh giá mô hình trên tập kiểm tra bằng RMSE
predictions = model.transform(test_data)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
rmse = evaluator.evaluate(predictions)
print("Root Mean Squared Error (RMSE) on test data = " + str(rmse))

# Hiển thị các dự đoán trên tập kiểm tra
predictions.show(truncate=False)
# from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
#
# # Xây dựng grid search cho các siêu tham số cần tinh chỉnh
# paramGrid = ParamGridBuilder() \
#     .addGrid(als.maxIter, [5, 10, 15]) \
#     .addGrid(als.regParam, [0.01, 0.1, 1.0]) \
#     .addGrid(als.rank, [5, 10, 15]) \
#     .build()
#
# # Khởi tạo CrossValidator với ALS model, các tham số grid, và metric để đánh giá mô hình (RMSE)
# crossval = CrossValidator(estimator=als,
#                           estimatorParamMaps=paramGrid,
#                           evaluator=evaluator,
#                           numFolds=3)  # Số lần chia tập dữ liệu (fold) trong Cross-Validation
#
# # Huấn luyện mô hình với Cross-Validator và dữ liệu huấn luyện
# cvModel = crossval.fit(training_data)
#
# # Lấy mô hình tốt nhất từ Cross-Validator
# best_model = cvModel.bestModel
#
# # In ra các siêu tham số tốt nhất được tìm thấy
# print("Best MaxIter: ", best_model._java_obj.parent().getMaxIter())
# print("Best RegParam: ", best_model._java_obj.parent().getRegParam())
# print("Best Rank: ", best_model._java_obj.parent().getRank())
#
# # Đánh giá chất lượng dự đoán trên tập kiểm tra bằng RMSE
# predictions = best_model.transform(test_data)
# rmse = evaluator.evaluate(predictions)
# print("Root Mean Squared Error (RMSE) on test data = " + str(rmse))

# Best MaxIter:  15
# Best RegParam:  0.1
# Best Rank:  15
# Root Mean Squared Error (RMSE) on test data = 0.8109716344310653
from pyspark.sql.functions import explode
from pyspark.sql.functions import col
# Tạo danh sách 10 đề xuất phim hàng đầu cho mỗi người dùng
userRecs = model.recommendForAllUsers(10)

# Hiển thị 10 đề xuất phim hàng đầu cho một người dùng cụ thể (ví dụ, người dùng có userId = 1)
user1_recommendations = userRecs.filter(col("userId") == 1).select("recommendations")
user1_recommendations.show(truncate=False)

# Lấy 10 phim có đề xuất cao nhất cho tất cả các ID người dùng
userRecs.show(truncate=False)


# Nhập userId mới từ người dùng
from pyspark.sql.functions import col, lit

# Lấy userId mới từ người dùng
new_user_id = int(input("Nhập userId mới: "))

# Tạo DataFrame chứa các bộ phim mà người dùng mới chưa đánh giá
existing_movie_ids = csv_data.filter(col("userId") == new_user_id).select("movieId")
all_movie_ids = csv_data.select("movieId").distinct()
new_user_movie_ids = all_movie_ids.subtract(existing_movie_ids).withColumn("userId", lit(new_user_id))

# Dự đoán đánh giá cho các bộ phim chưa đánh giá của người dùng mới
new_user_predictions = model.transform(new_user_movie_ids)

# Sắp xếp theo cột "prediction" giảm dần và giới hạn chỉ hiển thị 10 bản ghi đầu tiên
new_user_recommendations = new_user_predictions.select("movieId", "prediction").orderBy("prediction", ascending=False).limit(10)

# Hiển thị 10 bộ phim đề xuất cao nhất cho người dùng mới
new_user_recommendations.show(truncate=False)


def add_new_user(user_id, movie_id, rating):
    # Tạo DataFrame tạm thời với các cột chính (movieId, userId, rating)
    new_user_data = spark.createDataFrame([(movie_id, user_id, rating)], schema=["movieId", "userId", "rating"])

    # Thêm các cột với giá trị mặc định hoặc NULL
    new_user_data = new_user_data.withColumn("timestamp", lit(None).cast("timestamp"))
    new_user_data = new_user_data.withColumn("title", lit(None).cast("string"))
    new_user_data = new_user_data.withColumn("genres", lit(None).cast("string"))

    # Gộp DataFrame mới vào csv_data
    global csv_data
    csv_data = csv_data.union(new_user_data)

def add_new_user(user_id, movie_id, rating):
    # Tạo DataFrame tạm thời với các cột chính (movieId, userId, rating)
    new_user_data = spark.createDataFrame([(movie_id, user_id, rating)], schema=["movieId", "userId", "rating"])

    # Thêm các cột với giá trị mặc định hoặc NULL
    new_user_data = new_user_data.withColumn("timestamp", lit(None).cast("timestamp"))
    new_user_data = new_user_data.withColumn("title", lit(None).cast("string"))
    new_user_data = new_user_data.withColumn("genres", lit(None).cast("string"))

    # Gộp DataFrame mới vào csv_data
    global csv_data
    csv_data = csv_data.union(new_user_data)

# Hàm đưa ra top n phim phù hợp dựa trên thông tin rating của user
def recommend_movies_for_user(user_id, n=10):
    user_rec_df = model.recommendForUserSubset(csv_data.filter(col("userId") == user_id), n)
    return user_rec_df.select("recommendations.movieId")

# Hàm đưa ra rating cho một bộ phim cụ thể dựa trên thông tin rating của user
def predict_rating_for_movie(user_id, movie_id):
    prediction = model.transform(spark.createDataFrame([(movie_id, user_id)], schema=["movieId", "userId"])).collect()[0]["prediction"]
    return prediction
new_user_id = int(input("Nhập userId mới: "))
new_movies_id = int(input("Nhập moviesId: "))
new_rating = int(input("Nhập rating: "))
# Sử dụng các hàm đã định nghĩa
add_new_user(new_user_id, new_movies_id, new_rating)
recommended_movies = recommend_movies_for_user(new_user_id, 10)
predicted_rating = predict_rating_for_movie(new_user_id, new_movies_id)

# Hiển thị kết quả
recommended_movies.show(truncate=False)
print("Predicted rating for movie 456:", predicted_rating)

