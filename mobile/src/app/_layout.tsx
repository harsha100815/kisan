import { Stack, useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useCallback, useEffect, useMemo, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { ActivityIndicator, View } from 'react-native';
import { LanguageContext, type LanguageCode } from '../i18n';
import { colors } from '../theme/tokens';

const LANG_KEY = 'kisan.lang';

export default function RootLayout() {
  const [lang, setLangState] = useState<LanguageCode>('hi');
  const [ready, setReady] = useState(false);
  const router = useRouter();

  useEffect(() => {
    AsyncStorage.getItem(LANG_KEY)
      .then((saved) => {
        if (saved === 'hi' || saved === 'en') {
          setLangState(saved);
          // Returning user: skip language selection
          router.replace('/(tabs)/prices');
        }
      })
      .finally(() => setReady(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setLang = useCallback((l: LanguageCode) => {
    setLangState(l);
    void AsyncStorage.setItem(LANG_KEY, l);
  }, []);

  const value = useMemo(() => ({ lang, setLang }), [lang, setLang]);

  if (!ready) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.primary }}>
        <ActivityIndicator color="#FFFFFF" size="large" />
      </View>
    );
  }

  return (
    <LanguageContext.Provider value={value}>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </LanguageContext.Provider>
  );
}
