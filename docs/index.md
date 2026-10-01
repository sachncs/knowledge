<div class="kn-docs-home" markdown="1">

<section class="kn-hero">
<div class="kn-hero-copy">
<p class="kn-eyebrow">KNOWLEDGE / DOCUMENTATION</p>

<h1>Documentation</h1>

<p class="kn-intro">Turn a source into a bundle you can read, review, and version. Start with the quick guide, then use the reference when you need detail.</p>

<div class="kn-actions"><a class="kn-button kn-button-primary" href="getting-started/">Get started <span aria-hidden="true">→</span></a><a class="kn-button kn-button-secondary" href="cli/">Browse the CLI</a></div>
</div>

<aside class="kn-bundle-preview" aria-label="Example knowledge bundle">
<div class="kn-preview-head"><span>FROM DOCUMENTATION</span><span>TO OKF BUNDLE</span></div>
<div class="kn-preview-source"><span class="kn-status-dot"></span> developer.guide / setup</div>
<div class="kn-preview-rule"></div>
<p class="kn-tree-label">A folder of linked Markdown</p>
<ul class="kn-file-tree">
<li><span class="kn-tree-branch">├─</span><span class="kn-file-index">index.md</span><span class="kn-tree-note">entry point</span></li>
<li><span class="kn-tree-branch">├─</span><span>installation.md</span></li>
<li><span class="kn-tree-branch">├─</span><span>configuration.md</span></li>
<li><span class="kn-tree-branch">└─</span><span>first-project.md</span></li>
</ul>
<div class="kn-preview-foot"><span>plain text</span><span>·</span><span>relative links</span><span>·</span><span>versionable</span></div>
</aside>
</section>

<p class="kn-home-link"><a href="https://sachncs.github.io/knowledge/">← Product home</a><span>Alpha release · v0.1.0</span></p>

<section class="kn-section" id="start-here">
<div class="kn-section-head"><p class="kn-eyebrow">01 / START HERE</p><h2>Make your first bundle.</h2><p>Install the SDK, choose a model provider, and run your first extraction.</p></div>
<div class="kn-link-grid kn-grid-three">
<a class="kn-link-card" href="getting-started/"><span class="kn-card-index">01</span><strong>Getting started <span aria-hidden="true">↗</span></strong><span>Install, configure, and create a bundle.</span></a>
<a class="kn-link-card" href="concepts/"><span class="kn-card-index">02</span><strong>Core concepts <span aria-hidden="true">↗</span></strong><span>See how source sections become linked concepts.</span></a>
<a class="kn-link-card" href="tutorials/"><span class="kn-card-index">03</span><strong>Tutorials <span aria-hidden="true">↗</span></strong><span>Follow practical workflows from URL to update.</span></a>
</div>
</section>

<section class="kn-section" id="reference">
<div class="kn-section-head"><p class="kn-eyebrow">02 / REFERENCE</p><h2>Look up a detail.</h2></div>
<div class="kn-link-grid kn-grid-two">
<a class="kn-link-card kn-link-compact" href="cli/"><strong>CLI reference <span aria-hidden="true">↗</span></strong><span>Commands, flags, and examples.</span></a>
<a class="kn-link-card kn-link-compact" href="api/"><strong>Python API <span aria-hidden="true">↗</span></strong><span>Classes and methods generated from the source.</span></a>
<a class="kn-link-card kn-link-compact" href="configuration/"><strong>Configuration <span aria-hidden="true">↗</span></strong><span>Model selection, credentials, and settings.</span></a>
<a class="kn-link-card kn-link-compact" href="architecture/"><strong>Architecture <span aria-hidden="true">↗</span></strong><span>How reading, extraction, and writing fit together.</span></a>
</div>
</section>

<section class="kn-section kn-project-section" id="project">
<div class="kn-section-head"><p class="kn-eyebrow">03 / PROJECT</p><h2>Work with the project.</h2><p>Release notes, contribution guides, and project policies.</p></div>
<div class="kn-project-links"><a href="changelog/">Changelog <span>↗</span></a><a href="roadmap/">Roadmap <span>↗</span></a><a href="contributing/">Contributing <span>↗</span></a><a href="security/">Security policy <span>↗</span></a></div>
</section>

<section class="kn-install-section" id="install">
<div><p class="kn-eyebrow">QUICK START</p><h2>Ready to try it?</h2><p>Install the package, set a provider key, and point it at a documentation page.</p></div>
<div class="kn-install" markdown="1">

```sh
pip install knowledge
export OPENAI_API_KEY="your-api-key"
knowledge create https://example.com/docs.html ./docs-bundle
```

</div>
</section>

</div>
