import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, RefreshControl, StyleSheet, Text, View } from 'react-native';
import { api, type PriceRow } from '../../api/client';
import { useT } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

/** Today's mandi prices — live from GET /prices/today (stub source for now). */
export default function PricesScreen() {
  const t = useT();
  const [rows, setRows] = useState<PriceRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setError(false);
    try {
      const data = await api.pricesToday();
      setRows(data.rows);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <View style={[styles.container, styles.center]}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.error}>{t('prices.error')}</Text>
        <Text style={styles.retry} onPress={() => void load()}>
          {t('prices.retry')}
        </Text>
      </View>
    );
  }

  return (
    <FlatList
      style={styles.container}
      contentContainerStyle={styles.list}
      data={rows}
      keyExtractor={(r) => `${r.market}-${r.commodity}-${r.variety ?? ''}`}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); void load(); }} />
      }
      ListHeaderComponent={<Text style={styles.updated}>{t('prices.updated')}</Text>}
      renderItem={({ item }) => (
        <View style={styles.card}>
          <View style={styles.rowTop}>
            <Text style={styles.commodity}>{item.commodity}</Text>
            <Text style={styles.modal}>₹{item.modal_price.toLocaleString('en-IN')}</Text>
          </View>
          <Text style={styles.meta}>
            {item.market} · {item.district}, {item.state}
          </Text>
          <Text style={styles.range}>
            {t('prices.range')}: ₹{item.min_price.toLocaleString('en-IN')} – ₹
            {item.max_price.toLocaleString('en-IN')}
          </Text>
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  list: { padding: spacing.md, gap: spacing.md },
  center: { alignItems: 'center', justifyContent: 'center' },
  updated: { fontSize: fontSize.small, color: colors.textMuted, marginBottom: spacing.sm },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.border,
    gap: spacing.xs,
  },
  rowTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  commodity: { fontSize: fontSize.body + 2, fontWeight: '700', color: colors.text },
  modal: { fontSize: fontSize.body + 4, fontWeight: '700', color: colors.primary },
  meta: { fontSize: fontSize.body, color: colors.textMuted },
  range: { fontSize: fontSize.body, color: colors.text },
  error: { fontSize: fontSize.body, color: colors.danger, textAlign: 'center' },
  retry: { fontSize: fontSize.body, color: colors.primary, fontWeight: '700', marginTop: spacing.md },
});
