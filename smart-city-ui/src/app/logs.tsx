import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';

// CRITICAL: Replace with your actual IPv4 address
const API_BASE_URL = 'http://192.168.1.5:5000/api'; 

export default function MaintenanceScreen() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/maintenance/details`);
        setLogs(response.data);
      } catch (error) {
        console.error("Error fetching logs:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
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
        <Text style={styles.headerTitle}>Repair History</Text>
        <Text style={styles.headerSubtitle}>PostgreSQL Maintenance Logs</Text>
      </View>

      <FlatList
        data={logs}
        keyExtractor={(item) => item.log_id.toString()}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 20 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            {/* Card Header with Wrench Icon and Pill Badge */}
            <View style={styles.cardHeader}>
              <View style={styles.nodeContainer}>
                <Ionicons name="build" size={20} color="#475569" />
                <Text style={styles.nodeText}>{item.sensor_type}</Text>
              </View>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{item.node_id}</Text>
              </View>
            </View>

            {/* Log Details Stack */}
            <View style={styles.logDetails}>
              <View style={styles.detailRow}>
                <Ionicons name="clipboard-outline" size={22} color="#6366f1" />
                <View style={styles.textStack}>
                  <Text style={styles.detailLabel}>Action Taken</Text>
                  <Text style={styles.detailValue}>{item.action_taken}</Text>
                </View>
              </View>

              <View style={styles.detailRow}>
                <Ionicons name="person-outline" size={22} color="#10b981" />
                <View style={styles.textStack}>
                  <Text style={styles.detailLabel}>Technician</Text>
                  <Text style={styles.detailValue}>{item.technician_name}</Text>
                </View>
              </View>

              <View style={styles.detailRow}>
                <Ionicons name="calendar-outline" size={22} color="#f59e0b" />
                <View style={styles.textStack}>
                  <Text style={styles.detailLabel}>Date</Text>
                  <Text style={styles.detailValue}>{new Date(item.log_date).toLocaleDateString()}</Text>
                </View>
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
    elevation: 4, 
    shadowColor: '#0f172a', 
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 12,
  },
  
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  nodeContainer: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  nodeText: { fontSize: 16, fontWeight: '600', color: '#334155' },
  
  badge: { backgroundColor: '#e0f2fe', paddingVertical: 4, paddingHorizontal: 10, borderRadius: 12 },
  badgeText: { color: '#0369a1', fontSize: 12, fontWeight: '700' },
  
  logDetails: { gap: 14 },
  detailRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  textStack: { flex: 1 },
  detailLabel: { fontSize: 12, fontWeight: '500', color: '#94a3b8', marginBottom: 2 },
  detailValue: { fontSize: 15, fontWeight: '600', color: '#0f172a' },
});