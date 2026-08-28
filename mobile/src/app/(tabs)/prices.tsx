import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { api, type PriceRow } from '../../api/client';
import { useT } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

/** Today's mandi prices — live from GET /prices/today, with search filter. */
export default function PricesScreen() {
  const t = useT();
  const [rows, setRows] = useState<PriceRow[]>([]);
  const [query, setQuery] = useState('');
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

  const q = query.trim().toLowerCase();
  const filtered = q
    ? rows.filter(
        (r) =>
          r.commodity.toLowerCase().includes(q) ||
          r.market.toLowerCase().includes(q) ||
          r.state.toLowerCase().includes(q),
      )
    : rows;

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
      data={filtered}
      keyExtractor={(r, i) => `${r.market}-${r.commodity}-${r.variety ?? ''}-${i}`}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => {
            setRefreshing(true);
            void load();
          }}
        />
      }
      ListHeaderComponent={
        <View style={styles.header}>
          <TextInput
            style={styles.search}
            placeholder={t('prices.search')}
            placeholderTextColor={colors.textMuted}
            value={query}
            onChangeText={setQuery}
            returnKeyType="search"
          />
          <Text style={styles.updated}>
            {filtered.length} · {t('prices.updated')}
          </Text>
        </View>
      }
      ListEmptyComponent={<Text style={styles.empty}>{t('prices.no_match')}</Text>}
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
  center: { alignItems: 'center', justifyContent: 'center', padding: spacing.md },
  header: { gap: spacing.sm, marginBottom: spacing.xs },
  search: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm + 2,
    fontSize: fontSize.body,
    color: colors.text,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.border,
  },
  updated: { fontSize: fontSize.small, color: colors.textMuted },
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
  empty: { fontSize: fontSize.body, color: colors.textMuted, textAlign: 'center', marginTop: spacing.xl },
  error: { fontSize: fontSize.body, color: colors.danger, textAlign: 'center' },
  retry: { fontSize: fontSize.body, color: colors.primary, fontWeight: '700', marginTop: spacing.md },
});
