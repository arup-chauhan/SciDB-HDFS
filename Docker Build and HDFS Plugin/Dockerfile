FROM arup26/scidb:19.11-xenial

# Fix old Intel repo & missing keys
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BAC6F0C353D04109 || true && \
    sed -i '/intel/d' /etc/apt/sources.list /etc/apt/sources.list.d/*.list || true

# Install build tools and Hadoop
RUN apt update && apt install -y cmake g++ make libxml2-dev openjdk-8-jdk wget && \
    wget https://archive.apache.org/dist/hadoop/core/hadoop-2.7.7/hadoop-2.7.7.tar.gz && \
    tar -xzf hadoop-2.7.7.tar.gz -C /usr/local && \
    ln -s /usr/local/hadoop-2.7.7 /usr/local/hadoop && \
    echo "export HADOOP_HOME=/usr/local/hadoop" >> /etc/profile && \
    echo "export LD_LIBRARY_PATH=\$HADOOP_HOME/lib/native:\$LD_LIBRARY_PATH" >> /etc/profile && \
    rm -f hadoop-2.7.7.tar.gz

# Copy prebuilt HDFS plugin
COPY hdfs_plugin/libhdfs.so /opt/scidb/19.11/lib/scidb/plugins/

# Add startup script
COPY start-all.sh /usr/local/bin/start-all.sh
RUN chmod +x /usr/local/bin/start-all.sh

ENTRYPOINT ["/usr/local/bin/start-all.sh"]
