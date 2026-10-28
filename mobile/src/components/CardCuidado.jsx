import React from 'react';
import { TouchableOpacity, Text, View, StyleSheet } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function CardCuidado({ titulo, subtexto, icone, cor, onPress }) {
  return (
    <TouchableOpacity style={[styles.card, { borderLeftColor: cor }]} onPress={onPress} activeOpacity={0.8}>
      <View style={styles.cardIcon}>
        <MaterialCommunityIcons name={icone} size={28} color={cor} />
      </View>
      <View style={styles.cardTextos}>
        <Text style={styles.cardTitulo}>{titulo}</Text>
        <Text style={styles.cardSubtexto}>{subtexto}</Text>
      </View>
      <MaterialCommunityIcons name="chevron-right" size={20} color="#999" />
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    padding: 18,
    borderRadius: 20,
    marginBottom: 15,
    alignItems: 'center',
    backgroundColor: '#fff',
    borderLeftWidth: 6,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardIcon: { marginRight: 15 },
  cardTextos: { flex: 1 },
  cardTitulo: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  cardSubtexto: { fontSize: 13, marginTop: 2, color: '#666' },
});