#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = process.cwd();
const readJson = name => JSON.parse(readFileSync(resolve(root, 'docs/data', name), 'utf8'));
const ilan = readJson('kvkk_ilan.json').ilanlar ?? [];
const bildirim = readJson('kvkk_bildirim.json').bildirimler ?? [];
const fail = [];
const latestMonth = [...new Set(ilan.map(row => String(row.tarih ?? '').slice(0, 7)).filter(Boolean))].sort().at(-1);

if (!latestMonth) fail.push('İlan verisinde geçerli tarih bulunamadı.');

const isPlaceholder = value => !value || ['belirtilmedi', 'ilgili kvkk duyurusunda yer alır', 'detay bilgiye erişilemedi'].includes(String(value).trim().toLocaleLowerCase('tr-TR'));
const current = ilan.filter(row => String(row.tarih).startsWith(latestMonth));

for (const day of current) {
  const details = bildirim.filter(row => row.tarih === day.tarih);
  const expected = Number(day.bildirim);
  if (!Number.isInteger(expected) || expected < 0) fail.push(`${day.tarih}: geçerli ilan sayısı yok.`);
  if (details.length !== expected) fail.push(`${day.tarih}: ilan ${expected}, ayrıntı kaydı ${details.length}.`);

  for (const row of details) {
    for (const field of ['veriSorumlusu', 'sektor', 'tur', 'etkilenenNot', 'karar', 'veriDetay']) {
      if (isPlaceholder(row[field])) fail.push(`${day.tarih} / ${row.id}: ${field} alanı eksik veya genel ifade içeriyor.`);
    }
    if (!/^https:\/\/www\.kvkk\.gov\.tr\/Icerik\//.test(String(row.url ?? ''))) {
      fail.push(`${day.tarih} / ${row.id}: doğrudan KVKK duyuru bağlantısı yok.`);
    }
  }
}

const urls = bildirim.filter(row => String(row.tarih).startsWith(latestMonth)).map(row => row.url);
if (new Set(urls).size !== urls.length) fail.push(`${latestMonth}: aynı KVKK duyuru bağlantısı birden fazla kez kullanılmış.`);

if (fail.length) {
  console.error('KVKK veri doğrulaması başarısız:\n- ' + fail.join('\n- '));
  process.exit(1);
}

console.log(`KVKK veri doğrulaması başarılı: ${latestMonth} için ${current.reduce((sum, row) => sum + Number(row.bildirim || 0), 0)} duyuru ve ${bildirim.filter(row => String(row.tarih).startsWith(latestMonth)).length} ayrıntı kaydı doğrulandı.`);
