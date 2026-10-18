const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function fixture(response) {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id)) elements.set(id, { value: '', textContent: '', disabled: false,
      children: [], appendChild(child) { this.children.push(child); } });
    return elements.get(id);
  }
  const context = vm.createContext({
    document: { getElementById: element, createElement: () => ({}), addEventListener() {} },
    fetch: async () => response,
    setInterval() {}, Date
  });
  vm.runInContext(fs.readFileSync('static/js/app.js', 'utf8'), context);
  return { context, element };
}

test('HTTP failures display the error, retain input and allow retry', async () => {
  const { context, element } = fixture({ ok: false, status: 503,
    json: async () => ({ error: 'Local model unavailable' }) });
  element('chatInput').value = 'hello';
  await vm.runInContext('sendMessage()', context);
  assert.equal(element('chatMessages').children[1].textContent, 'Error: Local model unavailable');
  assert.equal(element('chatInput').value, 'hello');
  assert.equal(element('sendButton').disabled, false);
});

test('model output stays text and success identifies its real backend', async () => {
  const { context, element } = fixture({ ok: true,
    json: async () => ({ message: '<script>fixture</script>', model: 'qwen', demo: false }) });
  element('chatInput').value = 'hello';
  await vm.runInContext('sendMessage()', context);
  const answer = element('chatMessages').children[1];
  assert.equal(answer.textContent, '<script>fixture</script>');
  assert.equal(answer.innerHTML, undefined);
  assert.match(element('statusMessage').textContent, /qwen via local Ollama/);
});
