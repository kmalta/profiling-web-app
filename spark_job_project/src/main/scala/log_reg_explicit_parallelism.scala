
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


object LogRegExplicitParallelism {

  def printToFile(f: java.io.File)(op: java.io.PrintWriter => Unit) {
    val p = new java.io.PrintWriter(f)
    try { op(p) } finally { p.close() }
  }

  def main(args: Array[String]) {
    val num_features=args(0)
    val host_name=args(1)
    val host_port=args(2)
    val file_name=args(3)
    val iter_str=args(4)
    val explicit_parallelism=args(5)
    val file_path="hdfs://" + host_name + ":" + host_port + "/" + file_name

    val iterations = iter_str.toInt
    val conf = new SparkConf().setAppName("MlTest").set("spark.shuffle.blockTransferService", "nio")

    var warmstart_file_path=file_path + "_warmstart"


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
