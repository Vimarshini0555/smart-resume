document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    // DOM Elements
    const form = document.getElementById('analyze-form');
    const fileInput = document.getElementById('resume-file');
    const dropZone = document.getElementById('drop-zone');
    const fileStatus = document.getElementById('file-status');
    const dropZoneContent = document.querySelector('.drop-zone-content');
    const selectedFileName = document.getElementById('selected-file-name');
    const selectedFileSize = document.getElementById('selected-file-size');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const jobDescription = document.getElementById('job-description');
    const charCounter = document.getElementById('char-counter');
    const submitBtn = document.getElementById('submit-btn');
    const processingState = document.getElementById('processing-state');
    const processingStep = document.getElementById('processing-step');
    const progressBar = document.getElementById('progress-bar');
    
    // Result Dashboard DOM Elements
    const welcomePlaceholder = document.getElementById('welcome-placeholder');
    const dashboardContent = document.getElementById('dashboard-content');
    const scoreDisplay = document.getElementById('score-display');
    const scoreGaugeFill = document.getElementById('score-gauge-fill');
    const scoreRatingText = document.getElementById('score-rating-text');
    const scoreRatingDesc = document.getElementById('score-rating-desc');
    const resumeFilenameTag = document.getElementById('resume-filename-tag');
    const infoEmail = document.getElementById('info-email');
    const infoPhone = document.getElementById('info-phone');
    const infoLinkedin = document.getElementById('info-linkedin');
    const infoGithub = document.getElementById('info-github');
    const infoEmailItem = document.getElementById('info-email-item');
    const infoPhoneItem = document.getElementById('info-phone-item');
    const infoLinkedinItem = document.getElementById('info-linkedin-item');
    const infoGithubItem = document.getElementById('info-github-item');
    const checklistGrid = document.getElementById('checklist-grid');
    const jdMatchCard = document.getElementById('jd-match-card');
    const jdMatchBadge = document.getElementById('jd-match-badge');
    const jdMatchedSkillsCount = document.getElementById('jd-matched-skills-count');
    const jdMatchedSkills = document.getElementById('jd-matched-skills');
    const jdMissingSkillsCount = document.getElementById('jd-missing-skills-count');
    const jdMissingSkills = document.getElementById('jd-missing-skills');
    const jdMatchedKeywordsCount = document.getElementById('jd-matched-keywords-count');
    const jdMatchedKeywords = document.getElementById('jd-matched-keywords');
    const jdMissingKeywordsCount = document.getElementById('jd-missing-keywords-count');
    const jdMissingKeywords = document.getElementById('jd-missing-keywords');
    const skillsCategoryGrid = document.getElementById('skills-category-grid');
    const suggestionsList = document.getElementById('suggestions-list');
    const rawTextPreview = document.getElementById('raw-text-preview');
    const drawerTrigger = document.getElementById('drawer-trigger');
    const drawerContent = document.getElementById('drawer-content');
    const drawerChevron = document.getElementById('drawer-chevron');

    // Global state
    let selectedFile = null;

    // --- File Drag & Drop Handlers ---
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    dropZone.addEventListener('click', (e) => {
        // Trigger file input if clicking zone (but not inside remove-btn)
        if (e.target.closest('#remove-file-btn') || e.target.closest('.file-status')) {
            return;
        }
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        resetFileSelection();
    });

    function handleFileSelection(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showUploadError('Invalid format. Please select a PDF file.');
            return;
        }
        
        if (file.size > 16 * 1024 * 1024) {
            showUploadError('File is too large. Maximum size allowed is 16MB.');
            return;
        }

        selectedFile = file;
        selectedFileName.textContent = file.name;
        selectedFileSize.textContent = formatBytes(file.size);
        
        // Toggle drag-drop zone contents
        dropZoneContent.classList.add('hidden');
        fileStatus.classList.remove('hidden');
        dropZone.style.borderStyle = 'solid';
        dropZone.style.borderColor = 'rgba(6, 182, 212, 0.3)';
        dropZone.style.background = 'rgba(6, 182, 212, 0.02)';

        validateForm();
    }

    function resetFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        dropZoneContent.classList.remove('hidden');
        fileStatus.classList.add('hidden');
        dropZone.style.borderStyle = 'dashed';
        dropZone.style.borderColor = 'rgba(255, 255, 255, 0.15)';
        dropZone.style.background = 'rgba(255, 255, 255, 0.01)';
        
        // Return to welcome placeholder if file is cleared
        welcomePlaceholder.classList.remove('hidden');
        dashboardContent.classList.add('hidden');

        validateForm();
    }

    function showUploadError(msg) {
        alert(msg); // Elegant default alert, styled cleanly on standard system
        resetFileSelection();
    }

    // --- Job Description Textarea Handlers ---
    jobDescription.addEventListener('input', () => {
        const len = jobDescription.value.length;
        charCounter.textContent = `${len.toLocaleString()} chars`;
    });

    // --- Validation ---
    function validateForm() {
        if (selectedFile) {
            submitBtn.classList.remove('disabled');
            submitBtn.removeAttribute('disabled');
        } else {
            submitBtn.classList.add('disabled');
            submitBtn.setAttribute('disabled', 'true');
        }
    }

    // --- Utility Functions ---
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // --- Form Submission & Processing ---
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!selectedFile) return;

        // Show Processing Overlay
        processingState.classList.remove('hidden');
        
        // Progress Simulation Steps
        simulateProgress();

        const formData = new FormData();
        formData.append('resume', selectedFile);
        formData.append('job_description', jobDescription.value);

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Server error'); });
            }
            return response.json();
        })
        .then(data => {
            // End loading screen fast
            setTimeout(() => {
                processingState.classList.add('hidden');
                renderDashboard(data);
            }, 800);
        })
        .catch(err => {
            processingState.classList.add('hidden');
            alert(`Analysis failed: ${err.message}`);
        });
    });

    function simulateProgress() {
        const steps = [
            { limit: 25, label: "Extracting text structure from PDF..." },
            { limit: 55, label: "Analyzing essential layout blocks and headers..." },
            { limit: 80, label: "Classifying competencies against dynamic taxonomy..." },
            { limit: 95, label: "Correlating keywords with target requirements..." }
        ];

        let width = 0;
        progressBar.style.width = '0%';
        processingStep.textContent = "Starting analyzer components...";

        const interval = setInterval(() => {
            if (width >= 96) {
                clearInterval(interval);
            } else {
                width += Math.floor(Math.random() * 8) + 1;
                progressBar.style.width = `${Math.min(98, width)}%`;
                
                // Update descriptive label
                const currentStep = steps.find(s => width <= s.limit);
                if (currentStep) {
                    processingStep.textContent = currentStep.label;
                }
            }
        }, 150);
        
        // Attach listener to clear interval on finish
        form.addEventListener('submit', () => clearInterval(interval), { once: true });
    }

    // --- Dashboard Renderer ---
    function renderDashboard(data) {
        // Toggle elements
        welcomePlaceholder.classList.add('hidden');
        dashboardContent.classList.remove('hidden');

        // Set resume meta filename
        resumeFilenameTag.textContent = selectedFile.name;

        // 1. ATS Score Gauge Animation
        animateScore(data.ats_score);

        // 2. Candidate Information Card
        renderContactInfo(data.contact_info);

        // 3. Sections Checklist
        renderChecklist(data.sections);

        // 4. Job Description Match (Conditional)
        renderJDMatch(data.jd_analysis);

        // 5. Extracted Technical Competencies
        renderTechnicalSkills(data.skills);

        // 6. Suggestions
        renderSuggestions(data.suggestions);

        // 7. Parsed Text Preview
        rawTextPreview.textContent = data.raw_text_preview;
        
        // Re-trigger lucide icons
        lucide.createIcons();
    }

    function animateScore(targetScore) {
        // Score number animation counter
        let startVal = 0;
        const duration = 1200; // ms
        const stepTime = Math.abs(Math.floor(duration / targetScore));
        
        const counterInterval = setInterval(() => {
            if (startVal >= targetScore) {
                scoreDisplay.textContent = targetScore;
                clearInterval(counterInterval);
            } else {
                startVal++;
                scoreDisplay.textContent = startVal;
            }
        }, stepTime);

        // Circular dash fill
        // Stroke array length is 2 * PI * R = 2 * 3.1416 * 50 = 314.16
        const circleLength = 314.16;
        const offset = circleLength - (targetScore / 100) * circleLength;
        scoreGaugeFill.style.strokeDashoffset = offset;

        // Determine rating levels and colors
        let ratingText = "";
        let ratingDesc = "";
        let strokeColor = "";

        if (targetScore < 50) {
            ratingText = "Needs Refinement";
            ratingDesc = "Crucial structural or technical items are missing. Follow recommendations to optimize.";
            strokeColor = "url(#grad-danger)";
        } else if (targetScore >= 50 && targetScore < 75) {
            ratingText = "Good Potential";
            ratingDesc = "Excellent framework. Minor keyword alignments and metric additions will elevate match rates.";
            strokeColor = "url(#grad-warning)";
        } else {
            ratingText = "Highly ATS Ready";
            ratingDesc = "Superb keyword weight, structural components, and high-impact result verbs listed.";
            strokeColor = "url(#grad-success)";
        }

        scoreRatingText.textContent = ratingText;
        scoreRatingDesc.textContent = ratingDesc;
        
        // Setup SVG gradient colors
        setupGaugeGradients(strokeColor);
    }

    function setupGaugeGradients(activeStroke) {
        // Dynamically insert linear-gradients into SVGs if they don't exist
        let svg = document.querySelector('.radial-gauge');
        let defs = svg.querySelector('defs');
        
        if (!defs) {
            defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
            defs.innerHTML = `
                <linearGradient id="grad-danger" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#f87171" />
                    <stop offset="100%" stop-color="#fb923c" />
                </linearGradient>
                <linearGradient id="grad-warning" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#fbbf24" />
                    <stop offset="100%" stop-color="#f97316" />
                </linearGradient>
                <linearGradient id="grad-success" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#34d399" />
                    <stop offset="100%" stop-color="#06b6d4" />
                </linearGradient>
            `;
            svg.appendChild(defs);
        }
        scoreGaugeFill.setAttribute('stroke', activeStroke);
    }

    function renderContactInfo(info) {
        // Email
        if (info.email) {
            infoEmail.innerHTML = `<a href="mailto:${info.email}">${info.email}</a>`;
            infoEmailItem.classList.remove('opacity-muted');
        } else {
            infoEmail.textContent = "Not Found";
            infoEmailItem.classList.add('opacity-muted');
        }

        // Phone
        if (info.phone) {
            infoPhone.textContent = info.phone;
            infoPhoneItem.classList.remove('opacity-muted');
        } else {
            infoPhone.textContent = "Not Found";
            infoPhoneItem.classList.add('opacity-muted');
        }

        // LinkedIn
        if (info.linkedin) {
            // Clean link for display
            let cleanLink = info.linkedin.replace(/^(https?:\/\/)?(www\.)?/, '');
            if (cleanLink.length > 25) cleanLink = cleanLink.substring(0, 22) + '...';
            
            // Format link correctly with protocol
            let href = info.linkedin;
            if (!href.startsWith('http')) href = 'https://' + href;
            
            infoLinkedin.innerHTML = `<a href="${href}" target="_blank">${cleanLink}</a>`;
            infoLinkedinItem.classList.remove('opacity-muted');
        } else {
            infoLinkedin.textContent = "Not Listed";
            infoLinkedinItem.classList.add('opacity-muted');
        }

        // GitHub / Portfolio
        const portfolioLink = info.github || info.portfolio;
        if (portfolioLink) {
            let cleanLink = portfolioLink.replace(/^(https?:\/\/)?(www\.)?/, '');
            if (cleanLink.length > 25) cleanLink = cleanLink.substring(0, 22) + '...';
            
            let href = portfolioLink;
            if (!href.startsWith('http')) href = 'https://' + href;
            
            infoGithub.innerHTML = `<a href="${href}" target="_blank">${cleanLink}</a>`;
            infoGithubItem.classList.remove('opacity-muted');
            
            // Update icon dynamically
            const icon = info.github ? 'github' : 'globe';
            infoGithubItem.querySelector('i').setAttribute('data-lucide', icon);
        } else {
            infoGithub.textContent = "Not Listed";
            infoGithubItem.classList.add('opacity-muted');
            infoGithubItem.querySelector('i').setAttribute('data-lucide', 'github');
        }
    }

    function renderChecklist(sections) {
        checklistGrid.innerHTML = '';
        
        for (const [secName, found] of Object.entries(sections)) {
            const item = document.createElement('div');
            item.className = `check-item ${found ? 'found' : 'missing'}`;
            
            const icon = found ? 'check' : 'alert-circle';
            
            item.innerHTML = `
                <div class="check-icon-circle">
                    <i data-lucide="${icon}" size="14"></i>
                </div>
                <span class="check-name">${secName}</span>
            `;
            checklistGrid.appendChild(item);
        }
    }

    function renderJDMatch(jd) {
        if (!jd) {
            jdMatchCard.classList.add('hidden');
            return;
        }

        jdMatchCard.classList.remove('hidden');
        
        // Set Match Score Badge
        jdMatchBadge.textContent = `${jd.score}% Role Match`;
        
        // Color match badge based on score
        if (jd.score < 50) {
            jdMatchBadge.style.background = 'var(--gradient-danger)';
            jdMatchBadge.style.boxShadow = '0 0 15px rgba(248, 113, 113, 0.2)';
        } else if (jd.score >= 50 && jd.score < 75) {
            jdMatchBadge.style.background = 'var(--gradient-warning)';
            jdMatchBadge.style.boxShadow = '0 0 15px rgba(251, 191, 36, 0.2)';
        } else {
            jdMatchBadge.style.background = 'var(--gradient-success)';
            jdMatchBadge.style.boxShadow = '0 0 15px rgba(52, 211, 153, 0.2)';
        }

        // Render matched skills list
        jdMatchedSkillsCount.textContent = jd.matched_skills.length;
        jdMatchedSkills.innerHTML = '';
        if (jd.matched_skills.length > 0) {
            jd.matched_skills.forEach(skill => {
                jdMatchedSkills.appendChild(createSkillPill(skill, 'jd-pill-match'));
            });
        } else {
            jdMatchedSkills.innerHTML = '<span class="empty-placeholder-text">None found</span>';
        }

        // Render missing skills list
        jdMissingSkillsCount.textContent = jd.missing_skills.length;
        jdMissingSkills.innerHTML = '';
        if (jd.missing_skills.length > 0) {
            jd.missing_skills.forEach(skill => {
                jdMissingSkills.appendChild(createSkillPill(skill, 'jd-pill-missing'));
            });
        } else {
            jdMissingSkills.innerHTML = '<span class="empty-placeholder-text">Perfect skill coverage!</span>';
        }

        // Render matched keywords list
        jdMatchedKeywordsCount.textContent = jd.matched_keywords.length;
        jdMatchedKeywords.innerHTML = '';
        if (jd.matched_keywords.length > 0) {
            jd.matched_keywords.forEach(kw => {
                jdMatchedKeywords.appendChild(createSkillPill(kw, 'jd-pill-match'));
            });
        } else {
            jdMatchedKeywords.innerHTML = '<span class="empty-placeholder-text">None found</span>';
        }

        // Render missing keywords list
        jdMissingKeywordsCount.textContent = jd.missing_keywords.length;
        jdMissingKeywords.innerHTML = '';
        if (jd.missing_keywords.length > 0) {
            jd.missing_keywords.forEach(kw => {
                jdMissingKeywords.appendChild(createSkillPill(kw, 'jd-pill-missing'));
            });
        } else {
            jdMissingKeywords.innerHTML = '<span class="empty-placeholder-text">Excellent keyword density!</span>';
        }
    }

    function createSkillPill(name, customClass = '') {
        const pill = document.createElement('span');
        pill.className = `skill-pill ${customClass}`;
        pill.textContent = name;
        return pill;
    }

    function renderTechnicalSkills(skills) {
        skillsCategoryGrid.innerHTML = '';

        for (const [catName, skillList] of Object.entries(skills)) {
            const card = document.createElement('div');
            const isEmpty = skillList.length === 0;
            card.className = `skills-cat-card ${isEmpty ? 'empty-cat' : ''}`;
            
            // Set header
            const header = document.createElement('div');
            header.className = 'skills-cat-header';
            header.innerHTML = `
                <span class="skills-cat-title">${catName}</span>
                <span class="skills-cat-count">${skillList.length}</span>
            `;
            card.appendChild(header);

            // Set skills container
            const pillsContainer = document.createElement('div');
            pillsContainer.className = 'pills-container';

            if (!isEmpty) {
                skillList.forEach(skill => {
                    pillsContainer.appendChild(createSkillPill(skill));
                });
            } else {
                pillsContainer.innerHTML = '<span class="empty-placeholder-text">No matching tags extracted</span>';
            }

            card.appendChild(pillsContainer);
            skillsCategoryGrid.appendChild(card);
        }
    }

    function renderSuggestions(suggestions) {
        suggestionsList.innerHTML = '';

        suggestions.forEach(item => {
            const card = document.createElement('div');
            card.className = 'suggestion-item';
            
            const impactClass = `impact-${item.impact.toLowerCase()}`;
            
            card.innerHTML = `
                <button class="suggestion-header">
                    <div class="suggestion-title-area">
                        <span class="impact-badge ${impactClass}">${item.impact}</span>
                        <div class="suggestion-text-wrapper">
                            <span class="suggestion-cat-label">${item.category}</span>
                            <span class="suggestion-header-title" title="${item.title}">${item.title}</span>
                        </div>
                    </div>
                    <i data-lucide="chevron-down" class="chevron-icon" size="18"></i>
                </button>
                <div class="suggestion-body">
                    <p>${item.description}</p>
                </div>
            `;

            // Toggle Expand event
            const header = card.querySelector('.suggestion-header');
            header.addEventListener('click', () => {
                const isActive = card.classList.contains('active');
                
                // Collapse any active suggestion (optional accordion behavior)
                document.querySelectorAll('.suggestion-item').forEach(i => i.classList.remove('active'));
                
                if (!isActive) {
                    card.classList.add('active');
                }
            });

            suggestionsList.appendChild(card);
        });
    }

    // --- Drawer Trigger for raw text preview ---
    drawerTrigger.addEventListener('click', () => {
        const isHidden = drawerContent.classList.contains('hidden');
        if (isHidden) {
            drawerContent.classList.remove('hidden');
            drawerChevron.style.transform = 'rotate(180deg)';
        } else {
            drawerContent.classList.add('hidden');
            drawerChevron.style.transform = 'rotate(0deg)';
        }
    });
});
