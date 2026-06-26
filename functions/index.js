const { onRequest } = require('firebase-functions/v2/https');
const cors = require('cors')({ origin: true });

exports.generateExcuse = onRequest({ region: 'asia-northeast1', invoker: 'public' }, (req, res) => {
  cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: 'API key not configured' });
    }

    const { situation, detail } = req.body;

    const prompt = `あなたはユーモアのある言い訳の専門家です。
以下のシチュエーションに対して、笑えるけど少しリアリティのある言い訳を日本語で1つだけ生成してください。
言い訳の文章のみを返してください（説明や前置きは不要です）。

シチュエーション: ${situation}
${detail ? `補足: ${detail}` : ''}`;

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
          'content-type': 'application/json',
        },
        body: JSON.stringify({
          model: 'claude-haiku-4-5-20251001',
          max_tokens: 200,
          messages: [{ role: 'user', content: prompt }],
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        return res.status(response.status).json({ error: data.error?.message ?? 'API error' });
      }

      res.json({ excuse: data.content[0].text.trim() });
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });
});
