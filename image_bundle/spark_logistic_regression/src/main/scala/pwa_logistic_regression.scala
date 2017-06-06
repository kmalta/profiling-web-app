
import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.SparkContext._
import org.apache.spark.mllib.util.MLUtils

import org.apache.spark.mllib.classification.{LogisticRegressionModel, LogisticRegressionWithSGD, LogisticRegressionWithLBFGS}
import org.apache.spark.mllib.classification.{SVMModel, SVMWithSGD}
//import org.apache.spark.mllib.regression.{RidgeRegressionWithSGD, RidgeRegressionModel}
import org.apache.spark.mllib.evaluation.BinaryClassificationMetrics
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.evaluation.MulticlassMetrics
import org.apache.spark.mllib.linalg.{Vectors, Vector}
import org.apache.spark.ml.util.MLWriter
import org.apache.spark.storage.StorageLevel._

import sys.process.stringSeqToProcess


object PWALogisticRegression {

  def printToFile(f: java.io.File)(op: java.io.PrintWriter => Unit) {
    val p = new java.io.PrintWriter(f)
    try { op(p) } finally { p.close() }
  }

  def main(args: Array[String]) {
    val num_features=args(0)
    val file_name=args(1)
    val iter_str=args(2)
    val explicit_parallelism=args(3)
    val file_path="hdfs://master:9000/" + file_name
    val iterations = iter_str.toInt

    val conf = new SparkConf().setAppName("MlTest").set("spark.shuffle.blockTransferService", "nio")
    val sc = new SparkContext(conf)

    val data = MLUtils.loadLibSVMFile(sc, file_path, num_features.toInt, explicit_parallelism.toInt).persist(MEMORY_ONLY)
    val initialWeightsVec = Vectors.zeros(num_features.toInt)

    val setup_model = new LogisticRegressionWithSGD()
    setup_model.optimizer.setNumIterations(iterations)
    setup_model.optimizer.setConvergenceTol(0)
    val model = setup_model.run(data, initialWeightsVec)

    sc.stop()
  }
}
