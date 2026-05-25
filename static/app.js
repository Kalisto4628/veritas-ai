// Veritas AI — Frontend Javascript Logic

// Default Seed Sandbox Items (Fallback & Initial State)
const DEFAULT_SANDBOX_ITEMS = [
    {
        "text": "The Federal Reserve announced on Wednesday that it will maintain current interest rates, citing stable economic growth and moderate inflation.",
        "label": "REAL"
    },
    {
        "text": "SHOCKING: NASA scientists have secretly admitted that a massive asteroid is heading directly towards Earth, and they are hiding the truth!",
        "label": "FAKE"
    },
    {
        "text": "A new clinical trial published in the New England Journal of Medicine has revealed that a newly developed immunotherapy drug significantly increases survival rates.",
        "label": "REAL"
    },
    {
        "text": "Doctors are furious! This simple kitchen ingredient cures all forms of cancer in just 24 hours, but big pharma is trying to ban it.",
        "label": "FAKE"
    },
    {
        "text": "Microsoft announced today that it will invest $5 billion in building new carbon-neutral data centers across Europe by 2028.",
        "label": "REAL"
    },
    {
        "text": "BREAKING: Bill Gates is planning to install microchips in the global population using a mandatory new vaccine! Leaked documents reveal all.",
        "label": "FAKE"
    },
    {
        "text": "The Prime Minister declared a new environmental policy aimed at reducing single-use plastic waste by 80% over the next five years.",
        "label": "REAL"
    },
    {
        "text": "Unbelievable! Local police arrested a man who claims he traveled back in time from the year 2085 to warn us about an alien invasion.",
        "label": "FAKE"
    },
    {
        "text": "According to a report published by the World Health Organization, global vaccination campaigns have successfully eradicated polio in two more nations.",
        "label": "REAL"
    },
    {
        "text": "WARNING: Tap water in major cities is being spiked with mind-control chemicals to make the population submissive to new tax laws.",
        "label": "FAKE"
    },
    {
        "text": "Researchers at the Massachusetts Institute of Technology have developed a new solar cell design that achieves a record-breaking 28% efficiency.",
        "label": "REAL"
    },
    {
        "text": "The secret society Illuminati has officially launched a recruitment website, inviting members of the public to apply for wealth and power.",
        "label": "FAKE"
    }
];

// Application State
let state = {
    activeTab: 'tab-detector',
    sandboxItems: [...DEFAULT_SANDBOX_ITEMS],
    modelInfo: null,
    csvFile: null
};

// DOM Elements
const navItems = document.querySelectorAll('.nav-item');
const tabPanes = document.querySelectorAll('.tab-pane');
const wordCounter = document.getElementById('word-counter');
const newsTextInput = document.getElementById('news-text-input');
const btnClearText = document.getElementById('btn-clear-text');
const btnAnalyze = document.getElementById('btn-analyze');
const gaugeCircle = document.getElementById('gauge-circle');
const gaugeValue = document.getElementById('gauge-value');
const verdictBanner = document.getElementById('verdict-banner');
const verdictIcon = document.getElementById('verdict-icon');
const verdictText = document.getElementById('verdict-text');
const predictionDesc = document.getElementById('prediction-desc');
const detailedResultsSection = document.getElementById('detailed-results-section');
const highlightContainer = document.getElementById('highlighted-text-container');
const realIndicatorsList = document.getElementById('real-indicators-list');
const fakeIndicatorsList = document.getElementById('fake-indicators-list');
const analysisTabBtns = document.querySelectorAll('.analysis-tab-btn');
const subtabPanes = document.querySelectorAll('.subtab-pane');
const wordTooltip = document.getElementById('word-tooltip');

// Stylometrics DOM Elements
const metricCaps = document.getElementById('metric-caps');
const metricSubjectivity = document.getElementById('metric-subjectivity');
const metricReadability = document.getElementById('metric-readability');
const metricExclamation = document.getElementById('metric-exclamation');

// Sandbox DOM Elements
const sandboxTableBody = document.getElementById('sandbox-table-body');
const sandboxCount = document.getElementById('sandbox-count');
const btnSandboxAdd = document.getElementById('btn-sandbox-add');
const btnSandboxRetrain = document.getElementById('btn-sandbox-retrain');
const btnSandboxReset = document.getElementById('btn-sandbox-reset');
const sandboxText = document.getElementById('sandbox-text');
const sandboxLabel = document.getElementById('sandbox-label');

// CSV DOM Elements
const csvDropzone = document.getElementById('csv-dropzone');
const csvFileInput = document.getElementById('csv-file-input');
const selectedFileName = document.getElementById('selected-file-name');
const csvTextCol = document.getElementById('csv-text-col');
const csvLabelCol = document.getElementById('csv-label-col');
const csvSplitSlider = document.getElementById('csv-split-slider');
const splitValText = document.getElementById('split-val');
const btnCsvTrain = document.getElementById('btn-csv-train');
const csvReportBody = document.getElementById('csv-report-body');
const csvMetricsContainer = document.getElementById('csv-metrics-container');
const csvUploadForm = document.getElementById('csv-upload-form');

// CSV Metrics DOM
const csvAcc = document.getElementById('csv-acc');
const csvTestSize = document.getElementById('csv-test-size');
const csvVocabSize = document.getElementById('csv-vocab-size');
const csvPrecision = document.getElementById('csv-precision');
const csvRecall = document.getElementById('csv-recall');
const csvF1 = document.getElementById('csv-f1');
const csvPrecisionBar = document.getElementById('csv-precision-bar');
const csvRecallBar = document.getElementById('csv-recall-bar');
const csvF1Bar = document.getElementById('csv-f1-bar');
const cmTN = document.getElementById('cm-tn');
const cmFP = document.getElementById('cm-fp');
const cmFN = document.getElementById('cm-fn');
const cmTP = document.getElementById('cm-tp');
const cmCorrectTotal = document.getElementById('cm-correct-total');
const cmIncorrectTotal = document.getElementById('cm-incorrect-total');

// Model Stats DOM Elements
const infoVocab = document.getElementById('info-vocab');
const infoSamples = document.getElementById('info-samples');
const infoTimestamp = document.getElementById('info-timestamp');
const infoAlpha = document.getElementById('info-alpha');
const realWeightsTableBody = document.getElementById('real-weights-table-body');
const fakeWeightsTableBody = document.getElementById('fake-weights-table-body');
const widgetAccuracy = document.getElementById('widget-accuracy');
const widgetVocab = document.getElementById('widget-vocab');
const widgetSamples = document.getElementById('widget-samples');

// Initialize Lucide Icons
function initIcons() {
    lucide.createIcons();
}

// -------------------------------------------------------------
// TAB NAVIGATION SYSTEM
// -------------------------------------------------------------
function setupTabs() {
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
    
    // Sub-tabs inside Detector analysis pane
    analysisTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetSubtab = btn.getAttribute('data-subtab');
            
            analysisTabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            subtabPanes.forEach(pane => {
                if (pane.id === targetSubtab) {
                    pane.classList.add('active');
                } else {
                    pane.classList.remove('active');
                }
            });
        });
    });
}

function switchTab(tabId) {
    state.activeTab = tabId;
    
    // Update Sidebar Navigation state
    navItems.forEach(item => {
        if (item.getAttribute('data-tab') === tabId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Update Visible Tab Panes
    tabPanes.forEach(pane => {
        if (pane.id === tabId) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
    
    // Auto-fetch fresh model info on relevant tab activations
    if (tabId === 'tab-stats' || tabId === 'tab-sandbox') {
        fetchModelInfo();
    }
}

// -------------------------------------------------------------
// GAUGE CIRCLE COMPONENT
// -------------------------------------------------------------
let circumference = 0;
function initGauge() {
    const radius = gaugeCircle.r.baseVal.value;
    circumference = radius * 2 * Math.PI;
    gaugeCircle.style.strokeDasharray = `${circumference} ${circumference}`;
    setGaugeValue(0); // Neutral initial state
}

function setGaugeValue(percent, label = "REAL") {
    // Determine color based on veracity prediction
    if (percent === 0) {
        gaugeCircle.style.stroke = '#64748b'; // Slate Gray
        gaugeValue.textContent = '--%';
        gaugeCircle.style.strokeDashoffset = circumference;
        return;
    }
    
    const offset = circumference - (percent / 100) * circumference;
    gaugeCircle.style.strokeDashoffset = offset;
    gaugeValue.textContent = `${Math.round(percent)}%`;
    
    if (label === "REAL") {
        // Higher value = more green
        if (percent > 70) {
            gaugeCircle.style.stroke = '#10b981'; // Emerald
        } else if (percent > 50) {
            gaugeCircle.style.stroke = '#f59e0b'; // Gold
        } else {
            gaugeCircle.style.stroke = '#f97316'; // Orange
        }
    } else {
        // FAKE predictions: higher confidence means more red
        if (percent > 70) {
            gaugeCircle.style.stroke = '#ef4444'; // Crimson Red
        } else if (percent > 50) {
            gaugeCircle.style.stroke = '#f97316'; // Orange
        } else {
            gaugeCircle.style.stroke = '#f59e0b'; // Gold
        }
    }
}

// -------------------------------------------------------------
// NEWS DETECTOR FUNCTIONALITY
// -------------------------------------------------------------
function setupDetector() {
    // Word count tracking
    newsTextInput.addEventListener('input', () => {
        const text = newsTextInput.value.trim();
        const words = text ? text.split(/\s+/).length : 0;
        wordCounter.textContent = `${words} word${words !== 1 ? 's' : ''}`;
    });
    
    // Clear button
    btnClearText.addEventListener('click', () => {
        newsTextInput.value = '';
        wordCounter.textContent = '0 words';
        detailedResultsSection.classList.add('hidden');
        setGaugeValue(0);
        
        verdictBanner.className = 'verdict-tag neutral';
        verdictText.textContent = 'Ready for analysis';
        predictionDesc.textContent = 'Enter article text and press the Analyze button to extract model inferences.';
        
        // Reset indicator icons
        verdictIcon.setAttribute('data-lucide', 'alert-circle');
        initIcons();
    });
    
    // Sample loader
    document.querySelectorAll('.btn-sample').forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleType = btn.getAttribute('data-sample');
            loadSample(sampleType);
        });
    });
    
    // Predict trigger
    btnAnalyze.addEventListener('click', runPrediction);
}

const SAMPLE_TEXTS = {
    reuters: "The Federal Reserve declared on Wednesday that it will keep interest rates stable, pointing to a resilient labor market and moderate expansion in economic activity. In a official press release, the central bank committee stated they are committed to returning inflation to its 2% objective while maintaining full employment metrics. Market analysts noted the decision aligns with expectations.",
    conspiracy: "WARNING: A shocking secret document leaked from an insider meeting exposes a global plot to alter the weather and cause artificial crop failures. They are using hidden chemicals sprayed from airplanes to force private farmers into bankruptcy, allowing corporate elites to buy up all agricultural land. The media is completely silent about this truth! Share this warning with everyone!",
    miracle: "Doctors are furious! A natural home remedy made from baking soda, warm lemon juice, and a pinch of salt has been proven to cure all virus infections in less than 24 hours. The medical establishment is hiding this breakthrough discovery because it costs pennies and doesn't make massive profits for big pharmaceutical vaccine companies."
};

function loadSample(type) {
    if (SAMPLE_TEXTS[type]) {
        newsTextInput.value = SAMPLE_TEXTS[type];
        const words = newsTextInput.value.split(/\s+/).length;
        wordCounter.textContent = `${words} words`;
        
        // Auto click analyze
        runPrediction();
    }
}

async function runPrediction() {
    const text = newsTextInput.value.trim();
    if (!text || text.split(/\s+/).length < 5) {
        alert("Please enter a longer news article or headline (minimum 5 words) for a valid analysis.");
        return;
    }
    
    // UI Scanning Animation
    btnAnalyze.disabled = true;
    btnAnalyze.innerHTML = `<i class="spinner-icon"></i>Analyzing...`;
    
    // Simulate interactive ML evaluation scanning
    let progress = 10;
    const interval = setInterval(() => {
        progress += (90 - progress) * 0.3;
        setGaugeValue(progress, "REAL");
        gaugeValue.textContent = "SCAN";
    }, 100);
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        clearInterval(interval);
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Prediction request failed.");
        }
        
        const data = await response.json();
        
        // Show detailed card
        detailedResultsSection.classList.remove('hidden');
        
        // Render result values
        const confidencePercent = data.confidence * 100;
        
        if (data.label === "REAL") {
            setGaugeValue(confidencePercent, "REAL");
            
            if (confidencePercent > 80) {
                verdictBanner.className = "verdict-tag real";
                verdictText.textContent = "Highly Trustworthy";
                predictionDesc.textContent = `This text closely matches factual writing styles and objective reporting conventions. The model is ${Math.round(confidencePercent)}% confident that this is real news.`;
                verdictIcon.setAttribute('data-lucide', 'shield-check');
            } else {
                verdictBanner.className = "verdict-tag real";
                verdictText.textContent = "Partially Credible";
                predictionDesc.textContent = `The content shows moderate credibility but contains some subjective vocabulary. The model indicates a ${Math.round(confidencePercent)}% probability of being real.`;
                verdictIcon.setAttribute('data-lucide', 'info');
            }
        } else {
            // For FAKE predictions, the gauge will represent FAKE probability or we can display it nicely
            // Let's show the probability of it being FAKE as FAKE confidence
            setGaugeValue(confidencePercent, "FAKE");
            
            if (confidencePercent > 80) {
                verdictBanner.className = "verdict-tag fake";
                verdictText.textContent = "Spam / Deceptive";
                predictionDesc.textContent = `High density of sensationalism, emotional bias, and clickbait phrases detected. The model is ${Math.round(confidencePercent)}% confident that this content is fake or highly misleading.`;
                verdictIcon.setAttribute('data-lucide', 'x-circle');
            } else {
                verdictBanner.className = "verdict-tag fake";
                verdictText.textContent = "Potential Misinformation";
                predictionDesc.textContent = `The text contains mixed stylistic signals with notable emotional clickbait. Model flags this as suspicious with a ${Math.round(confidencePercent)}% probability of being fake.`;
                verdictIcon.setAttribute('data-lucide', 'alert-triangle');
            }
        }
        
        // Render word feature highlights
        renderHighlightedText(text, data.word_impacts);
        
        // Render Top Indicators lists
        renderIndicatorBadges(data.top_words_real, data.top_words_fake);
        
        // Render Stylometrics Heuristics
        renderStylometrics(data.stylometrics);
        
        initIcons();
        
        // Auto scroll to results
        detailedResultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (err) {
        clearInterval(interval);
        alert(`Analysis Error: ${err.message}`);
        setGaugeValue(0);
    } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = `<i data-lucide="wand-2"></i>Analyze Content`;
        initIcons();
    }
}

// -------------------------------------------------------------
// TEXT HIGHLIGHTER & TOOLTIPS
// -------------------------------------------------------------
function renderHighlightedText(rawText, wordImpacts) {
    highlightContainer.innerHTML = '';
    
    // Create an impact map for quick lookup
    const impactMap = {};
    wordImpacts.forEach(item => {
        impactMap[item.word.toLowerCase()] = {
            impact: item.impact,
            tfidf: item.tfidf,
            word: item.word
        };
    });
    
    // Split text preserving punctuation and spaces using regex
    const tokens = rawText.split(/(\s+)/);
    
    for (let i = 0; i < tokens.length; i++) {
        const token = tokens[i];
        if (!token.trim()) {
            // It's whitespace
            highlightContainer.appendChild(document.createTextNode(token));
            continue;
        }
        
        const cleanWord1 = token.toLowerCase().replace(/[^a-z0-9]/g, '');
        
        // Lookahead for bigram
        let bigramMatch = null;
        
        if (i + 2 < tokens.length) {
            // tokens[i+1] is whitespace, tokens[i+2] is the next word
            const nextToken = tokens[i+2];
            const cleanWord2 = nextToken.toLowerCase().replace(/[^a-z0-9]/g, '');
            const bigram = cleanWord1 + " " + cleanWord2;
            
            if (impactMap[bigram]) {
                bigramMatch = impactMap[bigram];
            }
        }
        
        if (bigramMatch) {
            // We matched a bigram!
            const spanText = tokens[i] + tokens[i+1] + tokens[i+2];
            const span = createImpactSpan(spanText, bigramMatch);
            highlightContainer.appendChild(span);
            i += 2; // Skip the next two tokens since we merged them into the span
        } else if (impactMap[cleanWord1] && cleanWord1.length > 0) {
            // Unigram match
            const span = createImpactSpan(token, impactMap[cleanWord1]);
            highlightContainer.appendChild(span);
        } else {
            // Normal un-modeled text node
            highlightContainer.appendChild(document.createTextNode(token));
        }
    }
}

function createImpactSpan(text, match) {
    const span = document.createElement('span');
    span.textContent = text;
    span.className = 'word-span';
    
    const impact = match.impact;
    const cleanWord = match.word;
    
    if (impact > 0) {
        if (impact > 0.15) span.classList.add('nb-real-4');
        else if (impact > 0.08) span.classList.add('nb-real-3');
        else if (impact > 0.03) span.classList.add('nb-real-2');
        else span.classList.add('nb-real-1');
    } else if (impact < 0) {
        const absImpact = Math.abs(impact);
        if (absImpact > 0.15) span.classList.add('nb-fake-4');
        else if (absImpact > 0.08) span.classList.add('nb-fake-3');
        else if (absImpact > 0.03) span.classList.add('nb-fake-2');
        else span.classList.add('nb-fake-1');
    }
    
    span.addEventListener('mouseenter', (e) => {
        showWordTooltip(e, cleanWord, match.tfidf, impact);
    });
    span.addEventListener('mousemove', (e) => {
        positionTooltip(e);
    });
    span.addEventListener('mouseleave', hideWordTooltip);
    
    return span;
}

function showWordTooltip(event, word, tfidf, impact) {
    const tooltipWord = document.getElementById('tooltip-word');
    const tooltipTfidf = document.getElementById('tooltip-tfidf');
    const tooltipImpact = document.getElementById('tooltip-impact');
    const tooltipDesc = document.getElementById('tooltip-desc');
    
    tooltipWord.textContent = word;
    tooltipTfidf.textContent = tfidf.toFixed(4);
    tooltipImpact.textContent = (impact > 0 ? '+' : '') + impact.toFixed(4);
    
    if (impact > 0) {
        tooltipDesc.textContent = "Word suggests REAL news.";
        tooltipDesc.className = "text-sm text-green";
        tooltipImpact.className = "text-green";
    } else {
        tooltipDesc.textContent = "Word suggests FAKE news.";
        tooltipDesc.className = "text-sm text-red";
        tooltipImpact.className = "text-red";
    }
    
    wordTooltip.classList.remove('hidden');
    positionTooltip(event);
}

function positionTooltip(event) {
    const tooltipWidth = wordTooltip.offsetWidth;
    const tooltipHeight = wordTooltip.offsetHeight;
    
    // Position tooltip 15px to the right and 15px below cursor
    let x = event.pageX + 15;
    let y = event.pageY + 15;
    
    // Prevent tooltip from overflowing the viewport width
    if (x + tooltipWidth > window.innerWidth) {
        x = event.pageX - tooltipWidth - 10;
    }
    
    wordTooltip.style.left = `${x}px`;
    wordTooltip.style.top = `${y}px`;
}

function hideWordTooltip() {
    wordTooltip.classList.add('hidden');
}

function renderIndicatorBadges(realWords, fakeWords) {
    realIndicatorsList.innerHTML = '';
    fakeIndicatorsList.innerHTML = '';
    
    if (realWords.length === 0) {
        realIndicatorsList.innerHTML = `<span class="text-sm text-dark">No significant real indicators.</span>`;
    } else {
        realWords.forEach(w => {
            const badge = document.createElement('span');
            badge.className = 'importance-badge real';
            badge.innerHTML = `${w.word} <span>+${w.impact.toFixed(3)}</span>`;
            realIndicatorsList.appendChild(badge);
        });
    }
    
    if (fakeWords.length === 0) {
        fakeIndicatorsList.innerHTML = `<span class="text-sm text-dark">No significant fake indicators.</span>`;
    } else {
        fakeWords.forEach(w => {
            const badge = document.createElement('span');
            badge.className = 'importance-badge fake';
            badge.innerHTML = `${w.word} <span>${w.impact.toFixed(3)}</span>`;
            fakeIndicatorsList.appendChild(badge);
        });
    }
}

function renderStylometrics(stylo) {
    metricCaps.textContent = `${stylo.uppercase_ratio}%`;
    metricSubjectivity.textContent = `${stylo.subjectivity_score}%`;
    metricReadability.textContent = `${Math.round(stylo.readability_score)}/100`;
    metricExclamation.textContent = stylo.exclamation_ratio.toFixed(1);
    
    // Add visual status styling classes if they exceed thresholds
    metricCaps.className = "stylo-val " + (stylo.uppercase_ratio > 10 ? "text-red" : "text-main");
    metricSubjectivity.className = "stylo-val " + (stylo.subjectivity_score > 6 ? "text-red" : (stylo.subjectivity_score > 3 ? "text-warning" : "text-green"));
    metricExclamation.className = "stylo-val " + (stylo.exclamation_ratio > 1.0 ? "text-red" : "text-main");
}

// -------------------------------------------------------------
// INTERACTIVE ML SANDBOX
// -------------------------------------------------------------
function setupSandbox() {
    renderSandboxTable();
    
    // Add document to sandbox set
    btnSandboxAdd.addEventListener('click', () => {
        const text = sandboxText.value.trim();
        const label = sandboxLabel.value;
        
        if (!text || text.split(/\s+/).length < 4) {
            alert("Please enter a news snippet of at least 4 words.");
            return;
        }
        
        state.sandboxItems.push({ text, label });
        sandboxText.value = '';
        
        renderSandboxTable();
    });
    
    // Reset corpus documents to default seed data
    btnSandboxReset.addEventListener('click', () => {
        if (confirm("Are you sure you want to reset the sandbox corpus back to the default seed documents?")) {
            state.sandboxItems = [...DEFAULT_SANDBOX_ITEMS];
            renderSandboxTable();
        }
    });
    
    // Live retrain on sandbox set
    btnSandboxRetrain.addEventListener('click', retrainSandboxModel);
}

function renderSandboxTable() {
    sandboxTableBody.innerHTML = '';
    sandboxCount.textContent = state.sandboxItems.length;
    
    state.sandboxItems.forEach((item, index) => {
        const row = document.createElement('tr');
        
        const labelCell = document.createElement('td');
        const labelSpan = document.createElement('span');
        labelSpan.className = `td-label-span ${item.label.toLowerCase()}`;
        labelSpan.textContent = item.label;
        labelCell.appendChild(labelSpan);
        
        const textCell = document.createElement('td');
        const textDiv = document.createElement('div');
        textDiv.className = 'text-truncate';
        textDiv.textContent = item.text;
        textDiv.title = item.text;
        textCell.appendChild(textDiv);
        
        const actionCell = document.createElement('td');
        const delBtn = document.createElement('button');
        delBtn.className = 'delete-btn-link';
        delBtn.innerHTML = `<i data-lucide="trash-2"></i>`;
        delBtn.addEventListener('click', () => {
            state.sandboxItems.splice(index, 1);
            renderSandboxTable();
        });
        actionCell.appendChild(delBtn);
        
        row.appendChild(labelCell);
        row.appendChild(textCell);
        row.appendChild(actionCell);
        
        sandboxTableBody.appendChild(row);
    });
    
    initIcons();
}

async function retrainSandboxModel() {
    if (state.sandboxItems.length < 4) {
        alert("The training corpus needs at least 4 documents to run a Naive Bayes train split.");
        return;
    }
    
    btnSandboxRetrain.disabled = true;
    btnSandboxRetrain.innerHTML = `<i class="spinner-icon"></i>Retraining...`;
    
    try {
        const response = await fetch('/api/train/sandbox', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: state.sandboxItems })
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Sandbox training failed.");
        }
        
        const data = await response.json();
        
        // Show success alert
        alert(`Model retrained successfully!\nAccuracy: ${(data.metrics.accuracy * 100).toFixed(2)}%\nVocabulary Size: ${data.model_info.vocab_size} words`);
        
        // Update widgets and state
        updateActiveModelWidgets(data.model_info);
        
    } catch (err) {
        alert(`Retraining Error: ${err.message}`);
    } finally {
        btnSandboxRetrain.disabled = false;
        btnSandboxRetrain.innerHTML = `<i data-lucide="play-circle"></i>Retrain Classifier`;
        initIcons();
    }
}

// -------------------------------------------------------------
// CSV TRAINING DATASET HUB
// -------------------------------------------------------------
function setupCSVHub() {
    // Range slider tracking
    csvSplitSlider.addEventListener('input', () => {
        splitValText.textContent = `${csvSplitSlider.value}%`;
    });
    
    // Drag & Drop event bindings
    ['dragenter', 'dragover'].forEach(eventName => {
        csvDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            csvDropzone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        csvDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            csvDropzone.classList.remove('dragover');
        }, false);
    });
    
    csvDropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleSelectedCSV(files[0]);
        }
    });
    
    csvDropzone.addEventListener('click', () => {
        csvFileInput.click();
    });
    
    csvFileInput.addEventListener('change', () => {
        if (csvFileInput.files.length > 0) {
            handleSelectedCSV(csvFileInput.files[0]);
        }
    });
    
    // Form submission
    csvUploadForm.addEventListener('submit', handleCSVSubmit);
}

function handleSelectedCSV(file) {
    if (!file.name.endsWith('.csv')) {
        alert("Invalid file format. Please select a valid comma-separated (.csv) file.");
        return;
    }
    
    state.csvFile = file;
    selectedFileName.textContent = file.name;
    selectedFileName.classList.add('text-green');
    btnCsvTrain.disabled = false;
}

async function handleCSVSubmit(event) {
    event.preventDefault();
    if (!state.csvFile) return;
    
    btnCsvTrain.disabled = true;
    btnCsvTrain.innerHTML = `<i class="spinner-icon"></i>Processing CSV & Training...`;
    
    const formData = new FormData();
    formData.append("file", state.csvFile);
    formData.append("text_column", csvTextCol.value.trim());
    formData.append("label_column", csvLabelCol.value.trim());
    formData.append("test_size", parseFloat(csvSplitSlider.value) / 100);
    
    try {
        const response = await fetch('/api/train/csv', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "CSV dataset training failed.");
        }
        
        const data = await response.json();
        
        // Show report details
        const placeholder = csvReportBody.querySelector('.report-placeholder');
        if (placeholder) placeholder.remove();
        
        csvMetricsContainer.classList.remove('hidden');
        
        // Render verification details
        const accuracyPct = data.metrics.accuracy * 100;
        const precisionPct = data.metrics.precision * 100;
        const recallPct = data.metrics.recall * 100;
        const f1Pct = data.metrics.f1_score * 100;
        
        csvAcc.textContent = `${accuracyPct.toFixed(1)}%`;
        csvTestSize.textContent = `${data.model_info.test_size_count} samples`;
        csvVocabSize.textContent = `${data.model_info.vocab_size} words`;
        
        csvPrecision.textContent = `${precisionPct.toFixed(1)}%`;
        csvRecall.textContent = `${recallPct.toFixed(1)}%`;
        csvF1.textContent = `${f1Pct.toFixed(1)}%`;
        
        csvPrecisionBar.style.width = `${precisionPct}%`;
        csvRecallBar.style.width = `${recallPct}%`;
        csvF1Bar.style.width = `${f1Pct}%`;
        
        // Confusion matrix values
        const cm = data.metrics.confusion_matrix;
        cmTN.textContent = cm.tn;
        cmFP.textContent = cm.fp;
        cmFN.textContent = cm.fn;
        cmTP.textContent = cm.tp;
        
        const totalCorrect = cm.tp + cm.tn;
        const totalIncorrect = cm.fp + cm.fn;
        cmCorrectTotal.textContent = totalCorrect;
        cmIncorrectTotal.textContent = totalIncorrect;
        
        alert("Success! The classifier has been trained on your custom CSV dataset.");
        
        // Update general status
        updateActiveModelWidgets(data.model_info);
        
    } catch (err) {
        alert(`CSV Training Failure: ${err.message}`);
    } finally {
        btnCsvTrain.disabled = false;
        btnCsvTrain.innerHTML = `<i data-lucide="cpu"></i>Train Model on CSV`;
        initIcons();
    }
}

// -------------------------------------------------------------
// MODEL INSIGHTS DATA LOAD
// -------------------------------------------------------------
async function fetchModelInfo() {
    try {
        const response = await fetch('/api/model/info');
        if (!response.ok) throw new Error("Could not load model info.");
        const data = await response.json();
        
        // Update state
        state.modelInfo = data;
        
        // Update general widgets
        updateActiveModelWidgets(data);
        
        // Populate stats tab
        infoVocab.textContent = `${data.vocab_size} words`;
        infoSamples.textContent = `${data.train_size} items`;
        infoTimestamp.textContent = data.train_date || "Untrained";
        infoAlpha.textContent = data.alpha;
        
        // Render weights tables
        renderWeightsTable(realWeightsTableBody, data.top_real);
        renderWeightsTable(fakeWeightsTableBody, data.top_fake);
        
    } catch (err) {
        console.error("Error retrieving model details:", err);
    }
}

function updateActiveModelWidgets(modelData) {
    const accPercent = (modelData.accuracy * 100).toFixed(2);
    widgetAccuracy.textContent = `${accPercent}%`;
    widgetVocab.textContent = `${modelData.vocab_size} words`;
    widgetSamples.textContent = `${modelData.train_size} items`;
}

function renderWeightsTable(tableBody, weightsList) {
    tableBody.innerHTML = '';
    
    if (weightsList.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No weights calculated.</td></tr>`;
        return;
    }
    
    weightsList.forEach((item, index) => {
        const row = document.createElement('tr');
        
        const rankCell = document.createElement('td');
        rankCell.textContent = `#${index + 1}`;
        
        const wordCell = document.createElement('td');
        wordCell.textContent = item.word;
        
        const realLogCell = document.createElement('td');
        realLogCell.textContent = item.real_log.toFixed(3);
        
        const fakeLogCell = document.createElement('td');
        fakeLogCell.textContent = item.fake_log.toFixed(3);
        
        row.appendChild(rankCell);
        row.appendChild(wordCell);
        row.appendChild(realLogCell);
        row.appendChild(fakeLogCell);
        
        tableBody.appendChild(row);
    });
}

// -------------------------------------------------------------
// APP BOOTSTRAP
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    initIcons();
    initGauge();
    setupTabs();
    setupDetector();
    setupSandbox();
    setupCSVHub();
    
    // Initial fetch of active model stats
    fetchModelInfo();
});
