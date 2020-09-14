start cmd.exe /k kafka_2.12-2.3.0/bin/windows/zookeeper-server-start.bat ../../config/zookeeper.properties
start cmd.exe /k kafka_2.12-2.3.0/bin/windows/kafka-server-start.bat ../../config/server.properties
start cmd.exe /k kafka_2.12-2.3.0/bin/windows/kafka-topics.bat --zookeeper localhost:2181 --topic twitterdata1 --create --partitions 1 --replication-factor 1
start cmd.exe /k kafka_2.12-2.3.0/bin/windows/kafka-console-consumer.bat --boostrap-server localhost:9092 --topic twitterdata1 --from-beginning


confluent .com download kafka