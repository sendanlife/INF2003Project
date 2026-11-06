import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import axios from 'axios';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons'; // Import Expo's built-in icons

const API_BASE_URL = 'http://192.168.1.5:5000/api'; 

export default function DashboardScreen() {
  const [analytics, setAnalytics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/telemetry/analytics`);
        setAnalytics(response.data);
      } catch (error) {
        console.error("Error fetching telemetry:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#0284c7" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.headerContainer}>
        <Text style={styles.headerTitle}>City Telemetry</Text>
        <Text style={styles.headerSubtitle}>Live NoSQL Aggregations</Text>
      </View>

      <FlatList
        data={analytics}
        keyExtractor={(item) => item._id}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 20 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            {/* Card Header with Icon and Pill Badge */}
            <View style={styles.cardHeader}>
              <View style={styles.nodeContainer}>
                <MaterialCommunityIcons name="access-point-network" size={22} color="#475569" />
                <Text style={styles.nodeText}>Node Status</Text>
              </View>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{item._id}</Text>
              </View>
            </View>

            {/* Metrics Grid */}
            <View style={styles.metricsGrid}>
              <View style={styles.metricBox}>
                <Ionicons name="thermometer-outline" size={24} color="#ef4444" />
                <Text style={styles.metricValue}>{item.avg_temp.toFixed(1)}°</Text>
                <Text style={styles.metricLabel}>Avg Temp</Text>
              </View>

              <View style={styles.metricBox}>
                <Ionicons name="water-outline" size={24} color="#0ea5e9" />
                <Text style={styles.metricValue}>{item.avg_humidity.toFixed(0)}%</Text>
                <Text style={styles.metricLabel}>Humidity</Text>
              </View>

              <View style={styles.metricBox}>
                <Ionicons name="pulse-outline" size={24} color="#10b981" />
                <Text style={styles.metricValue}>{item.reading_count}</Text>
                <Text style={styles.metricLabel}>Readings</Text>
              </View>
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, paddingHorizontal: 20, backgroundColor: '#f8fafc' },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
  
  headerContainer: { marginTop: 60, marginBottom: 20 },
  headerTitle: { fontSize: 28, fontWeight: '800', color: '#0f172a', letterSpacing: 0.5 },
  headerSubtitle: { fontSize: 14, fontWeight: '500', color: '#64748b', marginTop: 4 },
  
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    elevation: 4, // Android shadow
    shadowColor: '#0f172a', // iOS shadow
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
  },
  
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  nodeContainer: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  nodeText: { fontSize: 16, fontWeight: '600', color: '#334155' },
  
  badge: { backgroundColor: '#e0f2fe', paddingVertical: 4, paddingHorizontal: 10, borderRadius: 12 },
  badgeText: { color: '#0369a1', fontSize: 12, fontWeight: '700' },
  
  metricsGrid: { flexDirection: 'row', justifyContent: 'space-between' },
  metricBox: { alignItems: 'center', flex: 1 },
  metricValue: { fontSize: 20, fontWeight: '700', color: '#0f172a', marginTop: 8 },
  metricLabel: { fontSize: 12, fontWeight: '500', color: '#64748b', marginTop: 2 },
});