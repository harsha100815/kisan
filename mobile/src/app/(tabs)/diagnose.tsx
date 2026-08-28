import { useState } from 'react';
import { ActivityIndicator, Image, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { api, type DiagnosisResult } from '../../api/client';
import crops from '../../../../shared/domain/crops.json';
import { useLanguage, useT, type LanguageCode } from '../../i18n';
import { colors, fontSize, radius, spacing } from '../../theme/tokens';

type Crop = { key: string; name_en: string; name_hi: string };

const CROP_LIST = crops as Crop[];

/**
 * Photo-diagnosis flow. Every result follows the uncertainty contract:
 * preliminary only, confidence band shown, disclaimer always visible.
 */
export default function DiagnoseScreen() {
  const t = useT();
  const { lang } = useLanguage();
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [cropKey, setCropKey] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [error, setError] = useState(false);

  const cropName = (c: Crop, l: LanguageCode) => (l === 'hi' ? c.name_hi : c.name_en);

  const pick = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      const library = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!library.granted) return;
    }
    const shot = await ImagePicker.launchCameraAsync({ quality: 0.6, allowsEditing: false });
    let uri = shot.assets?.[0]?.uri ?? null;
    if (!uri) {
      const pickLib = await ImagePicker.launchImageLibraryAsync({ quality: 0.6, allowsEditing: false });
      uri = pickLib.assets?.[0]?.uri ?? null;
    }
    if (uri) {
      setImageUri(uri);
      setResult(null);
      setError(false);
    }
  };

  const analyze = async () => {
    if (!imageUri) return;
    setBusy(true);
    setError(false);
    try {
      setResult(await api.diagnose(imageUri, cropKey ?? undefined, lang));
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  };

  const bandLabel = (band: string | null) =>
    band === 'high' ? t('diag.confidence_high')
    : band === 'medium' ? t('diag.confidence_medium')
    : t('diag.confidence_low');

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{t('diag.title')}</Text>

      <Pressable style={styles.photoBox} onPress={() => void pick()}>
        {imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.preview} />
        ) : (
          <Text style={styles.photoHint}>{t('diag.take_photo')}</Text>
        )}
      </Pressable>

      <Text style={styles.section}>{t('diag.select_crop')}</Text>
      <View style={styles.cropWrap}>
        {CROP_LIST.map((c) => (
          <Pressable
            key={c.key}
            onPress={() => setCropKey(cropKey === c.key ? null : c.key)}
            style={[styles.chip, cropKey === c.key && styles.chipActive]}
          >
            <Text style={[styles.chipText, cropKey === c.key && styles.chipTextActive]}>
              {cropName(c, lang)}
            </Text>
          </Pressable>
        ))}
      </View>

      {imageUri && !result && !busy && (
        <Pressable style={styles.primaryBtn} onPress={() => void analyze()}>
          <Text style={styles.primaryBtnText}>{t('diag.check')}</Text>
        </Pressable>
      )}

      {busy && <ActivityIndicator size="large" color={colors.primary} style={styles.spinner} />}

      {error && <Text style={styles.error}>{t('diag.unavailable_body')}</Text>}

      {result && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>{t('diag.result_title')}</Text>
          {result.status === 'completed' && result.prediction ? (
            <>
              <Text style={styles.prediction}>{result.prediction.disease_key}</Text>
              <Text style={styles.band}>{bandLabel(result.confidence_band)}</Text>
              {result.alternatives.length > 0 && (
                <Text style={styles.alternatives}>
                  {result.alternatives.map((a) => a.disease_key).join(', ')}
                </Text>
              )}
            </>
          ) : (
            <Text style={styles.cardText}>{t('diag.unavailable_body')}</Text>
          )}
          <Text style={styles.disclaimer}>{t(result.disclaimer_key)}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.md, gap: spacing.md },
  title: { fontSize: fontSize.title, fontWeight: '700', color: colors.text },
  photoBox: {
    height: 220,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  preview: { width: '100%', height: '100%' },
  photoHint: { fontSize: fontSize.body, color: colors.textMuted, textAlign: 'center', padding: spacing.lg },
  section: { fontSize: fontSize.body, color: colors.textMuted, marginTop: spacing.xs },
  cropWrap: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  chip: {
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
  },
  chipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  chipText: { fontSize: fontSize.body, color: colors.text },
  chipTextActive: { color: '#FFFFFF' },
  primaryBtn: {
    backgroundColor: colors.primary,
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.xs,
  },
  primaryBtnText: { color: '#FFFFFF', fontSize: fontSize.body + 2, fontWeight: '700' },
  spinner: { marginVertical: spacing.lg },
  error: { fontSize: fontSize.body, color: colors.danger, textAlign: 'center' },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  cardTitle: { fontSize: fontSize.body, fontWeight: '700', color: colors.text },
  prediction: {
    fontSize: fontSize.body + 4,
    fontWeight: '700',
    color: colors.primary,
    textTransform: 'capitalize',
  },
  band: { fontSize: fontSize.body, color: colors.accent, fontWeight: '600' },
  alternatives: { fontSize: fontSize.small, color: colors.textMuted },
  cardText: { fontSize: fontSize.body, color: colors.textMuted },
  disclaimer: { fontSize: fontSize.small, color: colors.danger, marginTop: spacing.xs },
});
