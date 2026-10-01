<div class="kn-docs-home" markdown="1">

<p class="kn-eyebrow">GUIDES &amp; REFERENCE</p>

# Documentation

<p class="kn-intro"><strong>knowledge</strong> turns documentation sources into linked Markdown bundles. Use these guides to install the SDK, create and maintain bundles, and explore the Python API.</p>

<p class="kn-home-link"><a href="https://sachncs.github.io/knowledge/">← Product home</a><span>Alpha release · v0.1.0</span></p>

## Start here

<div class="kn-link-grid">
<a class="kn-link-card" href="getting-started/"><strong>Getting started</strong><span>Install, configure a model provider, and create a bundle.</span></a>
<a class="kn-link-card" href="concepts/"><strong>Core concepts</strong><span>Understand the OKF bundle structure and extraction flow.</span></a>
<a class="kn-link-card" href="tutorials/"><strong>Tutorials</strong><span>Follow practical workflows for URLs, local files, and updates.</span></a>
<a class="kn-link-card" href="troubleshooting/"><strong>Troubleshooting</strong><span>Find fixes for common setup and runtime issues.</span></a>
</div>

## Reference

<div class="kn-link-grid">
<a class="kn-link-card" href="cli/"><strong>CLI reference</strong><span>Commands, options, and examples.</span></a>
<a class="kn-link-card" href="api/"><strong>Python API</strong><span>Classes and methods generated from the source API.</span></a>
<a class="kn-link-card" href="configuration/"><strong>Configuration</strong><span>Model selection, credentials, and environment settings.</span></a>
<a class="kn-link-card" href="architecture/"><strong>Architecture</strong><span>How source reading, extraction, and bundle writing fit together.</span></a>
</div>

## Project

<div class="kn-link-grid">
<a class="kn-link-card" href="changelog/"><strong>Changelog</strong><span>Released changes and current work.</span></a>
<a class="kn-link-card" href="roadmap/"><strong>Roadmap</strong><span>Planned work and release milestones.</span></a>
<a class="kn-link-card" href="contributing/"><strong>Contributing</strong><span>How to report issues and propose changes.</span></a>
<a class="kn-link-card" href="security/"><strong>Security policy</strong><span>How to report a vulnerability privately.</span></a>
</div>

## Install

<div class="kn-install" markdown="1">

```sh
pip install knowledge
export OPENAI_API_KEY="your-api-key"
knowledge create https://example.com/docs.html ./docs-bundle
```

</div>

Set credentials for your chosen provider before running the CLI. See the [configuration guide](configuration.md) for other providers and local models.

</div>
