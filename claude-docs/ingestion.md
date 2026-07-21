# Rebuild Ingestion System

## 1. What It Does

The ingestion system downloads third-party software artifacts from their original sources and stores them in a configurable virtual filesystem (VFS). The primary purposes are:

- Guarantee a **local, durable copy** of upstream binaries that could disappear or change.
- Enforce **SHA-256 checksum verification** so stored artifacts can be trusted.
- Provide a **stable, versioned filename** for each artifact so build recipes can refer to it by name rather than by upstream URL.

The entry point is `bin/reingest.py`, which delegates to `ingest_cli`. Recipe files have the extension `.reingest`.

---

## 2. File Format — `.reingest`

Each `.reingest` file begins with the magic header `!rebuild.ingest.v1!` and contains one or more `entry` blocks plus optional file-level `variables`.

```
!rebuild.ingest.v1!

description
  "Sources for the JDK 21 LTS distribution"

variables
  BASE_URL = "https://download.java.net/java/GA/jdk21"

entry jdk 21.0.2
  description
    "OpenJDK 21.0.2 binaries"

  variables
    all: TARBALL = "openjdk-{VERSION}_linux-x64_bin.tar.gz"

  method http
    all: url = "{BASE_URL}/{VERSION}/openjdk-{VERSION}_linux-x64_bin.tar.gz"
    all: checksum = "sha256:abc123..."
    all: ingested_filename = "jdk/{VERSION}/{TARBALL}"
```

### Entry fields

| Field | Description |
|---|---|
| `name` | Logical name of the artifact (unique across all loaded `.reingest` files) |
| `version` | Version string — available as `{VERSION}` in variable substitutions |
| `description` | Human-readable description (optional) |
| `variables` | Per-entry key-value pairs; can be platform-masked |
| `data` | Opaque key-value substitution data (used by `recipe_data_manager`) |
| `method` | Download method block (`http` or `git`) |

### Variable substitution

Two builtins are always available: `{NAME}` and `{VERSION}`. File-level and entry-level `variables` blocks add more. Substitution uses bracket syntax `{KEY}`. Values in `method` blocks are resolved after all variable layers are merged.

### Platform masking

Any value in a `variables` or `method` block can be prefixed with a platform mask (`all`, `linux`, `macos`, `windows`, etc.):

```
  method http
    linux:  url = "https://example.com/{NAME}-{VERSION}-linux.tar.gz"
    macos:  url = "https://example.com/{NAME}-{VERSION}-darwin.tar.gz"
    linux:  checksum = "sha256:aaa..."
    macos:  checksum = "sha256:bbb..."
    all:    ingested_filename = "{NAME}/{VERSION}/{NAME}-{VERSION}.tar.gz"
```

The runner resolves values for the target system at download time.

---

## 3. Download Methods

### 3.1 `http`

Downloads a file over HTTP/HTTPS. Uses a SQLite-backed request cache (`requests-cache`) keyed by URL, stored at `~/.egoist/ingest/downloads/http_cache.sqlite`.

| Field | Required | Description |
|---|---|---|
| `url` | yes | Full URL of the artifact |
| `checksum` | yes | SHA-256 checksum of the downloaded file (`sha256:<hex>`) |
| `ingested_filename` | yes | Destination path within the VFS |
| `cookies` | no | Cookie key-value pairs for authenticated downloads |
| `arcname` | no | If set, the downloaded file is renamed to this name inside an archive before upload |

Checksum is verified immediately after download. Mismatch raises `ingest_error` and the upload never happens.

The `arcname` field supports a repack pattern: the downloaded file is placed inside a new archive under the given name (with execute bit set), useful when an upstream distributes a binary without a wrapper archive.

### 3.2 `git`

Clones a git repository and produces a reproducible tarball at a specific revision using `bat.git.git_archive_cache`.

| Field | Required | Description |
|---|---|---|
| `address` | yes | Git remote URL |
| `revision` | yes | Commit SHA, tag, or branch |
| `ingested_filename` | yes | Destination path within the VFS |

The cache avoids re-cloning the same repo across runs.

---

## 4. Module Structure

```
lib/rebuild/ingest/
  ingest_file.py               # Top-level parsed representation of a .reingest file
  ingest_file_parser.py        # Parses .reingest text into ingest_file
  ingest_entry.py              # Single entry (name, version, method, variables, data)
  ingest_entry_parser.py       # Parses an entry node; dispatches method descriptors
  ingest_entry_list.py         # Typed list of ingest_entry
  ingest_method.py             # Pairs a descriptor with its masked value list
  ingest_method_descriptor_base.py  # ABC: method(), fields(), download()
  ingest_method_descriptor_http.py  # HTTP download + checksum + repack
  ingest_method_descriptor_git.py   # Git clone + archive
  ingest_method_field.py       # Field descriptor (key, optional flag)
  ingest_project.py            # Loads all .reingest files under a directory tree
  ingest_runner.py             # Orchestrates load → resolve → download → upload
  ingest_cli_command.py        # CLI handler: run(), include/exclude filtering
  ingest_cli_options.py        # Options dataclass (systems, cache_dir, include, exclude)
  ingest_cli_options.py        # CLI option definitions (argparse)
  ingest_command_handler.py    # bcli_command_handler adapter
  ingest_command_factory.py    # Registers the ingest subcommand
  ingest_pypi.py               # PyPI JSON API helper — queries versions + checksums
  ingest_third_party_info.py   # PyPI project metadata (name, license, releases)
  ingest_third_party_release.py  # Single PyPI release (version, checksum, url)
  ingest_error.py              # Exception class
```

---

## 5. Execution Flow

```
reingest.py
  └─ ingest_cli.run()
       └─ ingest_command_handler._command_run(vfs_config, project_dir, args, ...)
            └─ ingest_cli_command.run()
                 1. vfs_registry.load_from_config_file(vfs_config)   → VFS instance
                 2. ingest_runner(fs, project_dir, args)
                 3. runner.load()
                      └─ ingest_project: walks dir tree, finds *.reingest,
                         parses each file, indexes entries by name
                 4. runner.ingest_all() / ingest_one() / ingest_some()
                      └─ for each entry:
                           a. resolve platform-specific variable substitutions
                           b. entry.download(system, global_vars, cache_dir, tmp_dir)
                                └─ method_descriptor.download(resolved_args)
                                    http: download → verify sha256 → optional repack
                                    git:  git_archive_cache.get_tarball(address, rev)
                           c. fs.upload_file(local_tmp, ingested_filename)
```

### Include / Exclude filtering

`--include name1 name2` — ingest only those entries (each must exist, error otherwise).  
`--exclude name1 name2` — ingest all entries except these.  
With neither flag, all entries in the project are ingested.

---

## 6. VFS / Storage Configuration

The runner receives a `vfs_fs` instance from `vfs_registry`, configured via a storage config file (e.g., `rebuild-recipes/config/storage.config`).

Current backends observed in the config:

| Backend | Provider key | Notes |
|---|---|---|
| pCloud | `pcloud` | Cloud storage; credentials via env var `$RAMIRO_PCLOUD_PASSWORD` |
| Local filesystem | `local` | Flat directory, e.g. `~/sources/local` |

The storage config format:

```
storage
  name: pcloud_ramiro
  provider: pcloud
  repo: rebuild_stuff
  download.username: pcloud_rebuild@fateware.com
  download.password: ${RAMIRO_PCLOUD_PASSWORD}
  upload.username: pcloud_rebuild@fateware.com
  upload.password: ${RAMIRO_PCLOUD_PASSWORD}
```

The `ingested_filename` field in each entry determines the path within the VFS, giving full control over the directory layout of the stored artifact.

---

## 7. PyPI Helper

`ingest_pypi` queries `https://pypi.org/pypi/<name>/json` to enumerate all releases of a PyPI package and extract `sdist` download URLs and SHA-256 checksums. This is a generation helper — it produces the data needed to author `.reingest` entries for Python packages, not part of the download/upload flow itself.

---

## 8. Issues and Concerns

### 8.1 No post-upload checksum verification

The system verifies the checksum of the downloaded file against the declared value before uploading. It does not re-verify what is actually stored on the VFS. If the upload is silently truncated or the VFS backend mangles the file, there is no detection.

**Fix:** after `fs.upload_file()`, call `fs.download_file()` to a temp location and re-verify the SHA-256, or have the VFS layer return a content hash from the upload call.

### 8.2 Checksums are hand-authored

The `checksum` field in each `.reingest` entry must be typed in by hand. There is no tooling to auto-populate it from the upstream source. A wrong or stale checksum silently breaks ingestion until someone runs it and notices the failure.

**Fix:** add a `reingest update-checksums` subcommand that downloads each artifact, computes its SHA-256, and patches the `.reingest` file in-place. `ingest_pypi` already retrieves PyPI checksums; the same pattern needs a generic HTTP equivalent.

### 8.3 Checksum format is inconsistent

The `checksum` field in `ingest_method_descriptor_http` is compared raw against `bf_checksum.checksum(...)` which returns a plain hex string. The recipe notation is `sha256:<hex>` in comments/docs but the parser does not strip the `sha256:` prefix — if someone includes it, the comparison will always fail silently.

**Fix:** normalize the checksum field at parse time: strip any `sha256:` / `sha1:` prefix and store algorithm + digest separately.

### 8.4 No dry-run mode implemented

`ingest_cli_options` has a `dry_run` field but `ingest_runner` and `ingest_cli_command` do not act on it — every run performs real downloads and uploads.

### 8.5 No version history in the VFS

The `ingested_filename` path encodes the version (e.g., `jdk/21.0.2/jdk-21.0.2.tar.gz`), so multiple versions coexist as separate paths. But:
- There is no index or manifest of what versions are stored.
- Deleting an old version from the VFS is a manual operation with no undo.
- The local download cache (`http_cache.sqlite`) is never pruned.

### 8.6 Single target system per run

`ingest_cli_options.systems` is a list but `ingest_runner.ingest_one` uses only `options.systems[0]`. Multi-system ingestion in one run is broken.

### 8.7 pCloud is not an appropriate long-term store for large binary artifacts

pCloud is a consumer cloud storage service. It works for small tarballs but is not suitable as the primary durable store for ISO images (500 MB–4 GB each). It has no native versioning, no content-addressable storage, and its API is non-standard.

---

## 9. Security Issues

### 9.1 Checksum is the only integrity mechanism — and it is optional

In `ingest_method_descriptor_http.download()`, the checksum check is guarded by `if checksum:`. An entry with an empty or missing `checksum` field will be downloaded and uploaded with no integrity check at all. This is a silent footgun: a recipe author who omits the checksum gets no warning.

**Fix:** make `checksum` a required field. Add a linter subcommand (`reingest lint`) that rejects entries without checksums.

### 9.2 Cookies are passed as plaintext in the recipe file

The `cookies` field in `http` entries is stored as plaintext key-value pairs in the `.reingest` file. If these cookies carry session tokens or authentication credentials, they are committed to the recipe repository in the clear.

**Fix:** integrate `bat.secret_vault` for cookie values, the same way the Proxmox framework handles credentials. Support `vault:path/key` references in the `cookies` field.

### 9.3 No TLS certificate validation override exists, but also no enforcement

The system relies on `bnet.http.http_session` for downloads. It is not clear whether TLS validation is enforced or can be disabled by caller options. If the session can be configured to skip TLS verification, a misconfigured run could silently accept a MITM-substituted file — the checksum is the last line of defense, not the transport.

**Fix:** audit `http_session` to confirm TLS verification cannot be disabled; document this explicitly.

### 9.4 Storage credentials in environment variables with no rotation mechanism

`$RAMIRO_PCLOUD_PASSWORD` is the only credential management in the current storage config. There is no vault integration, no rotation path, and no scoping — a process with access to the environment has full read/write access to the artifact store.

**Fix:** route storage credentials through `bat.secret_vault`, same pattern as the Proxmox framework.

---

## 10. Prior Art

### 10.1 What this system is closest to

**Bazel's `http_archive` / `http_file` rules** — declarative artifact fetching with mandatory SHA-256 checksums, stored in a content-addressable local cache. The rebuild ingest system is essentially the same concept but with an upload step to a remote VFS rather than a pure local cache.

**Nix `fetchurl` / `fetchFromGitHub`** — same philosophy: pinned URL + hash = reproducible fetch. Nix's store is content-addressable by hash; rebuild's store is path-addressable by version string.

**Homebrew formula `url`/`sha256` blocks** and **pkgbuild `source`/`sha256sums` arrays** (Arch Linux) — the same declarative pattern at the recipe level. The rebuild `.reingest` format is analogous.

### 10.2 Purpose-built artifact repository tools

| Tool | Notes |
|---|---|
| **JFrog Artifactory** | Full-featured; supports generic artifacts, Docker, Maven, PyPI, npm, etc. Built-in checksums, replication, access control. Heavy — requires a server and a license for the pro features. |
| **Sonatype Nexus Repository** | Similar scope to Artifactory. OSS version is free. Good for organizations already running Java CI. |
| **Pulp** | Open source, self-hosted. Supports generic content + multiple package types. Less polish than Artifactory but fully open. |
| **Zot** | OCI-native content store; can store arbitrary blobs via ORAS. Lightweight, open source, Apache 2.0. |

### 10.3 Content-addressable / archival stores

**IPFS** — content-addressable, decentralized, inherently verifiable. Good for immutable artifacts; poor ergonomics for version-named files and private storage.

**Restic / Borg** — backup tools, not artifact stores. Not a good fit for structured version-named retrieval.

**The Software Heritage Archive** — archives source code (git repos) at scale. Relevant as a fallback for source tarballs but not for binary artifacts.

---

## 11. Storage Options

The core requirements for the target use case (Linux ISO images, Java distros, Docker binaries, `uv`, and similar) are:

| Requirement | Implication |
|---|---|
| Local durable copy | Self-hosted or self-controlled storage; not just a CDN pointer |
| SHA-256 integrity | Must verify on both ingest and retrieval |
| Version history | Multiple versions of the same artifact must coexist; old versions must be recoverable |
| Large file support | ISOs are 500 MB–4 GB; Java distros 150–300 MB; tarballs 1–200 MB |
| Idempotent re-ingest | Re-running with the same inputs must be a no-op |

---

### 11.1 Git LFS (preferred by author)

**How it works:** Git LFS replaces large file contents with pointer files in the git tree; actual bytes are stored on an LFS server (GitHub, GitLab, Gitea, or a self-hosted `git-lfs` backend). History, versioning, and diffs on pointer files come for free from git. Content is addressed by SHA-256 in the pointer file.

**Pros:**
- Version history is the git log — trivially auditable and rollback-able.
- SHA-256 content addressing baked into the LFS pointer format.
- Familiar workflow (`git pull` gets you the files).
- Self-hostable with Gitea + local LFS storage; no cloud dependency.
- The rebuild ingest system can use an LFS-backed repo as its VFS target.

**Cons:**
- Linux ISO images (500 MB–4 GB) push into awkward territory: GitHub LFS has a 2 GB file limit and charges per GB of storage/bandwidth. GitLab LFS has a 5 GB limit on free tier.
- Self-hosted `git-lfs` (via Gitea) avoids cloud limits but requires running a git server.
- Cloning a repo with many multi-GB LFS objects is slow; `git lfs fetch --include` filtering helps but adds operational complexity.
- Git is not designed as a blob store; history of binary blobs grows linearly with no deduplication.

**Verdict:** Good fit for Java distros, Docker static binaries, tarballs (< 500 MB). Problematic for full Linux ISO images unless on self-hosted Gitea with no size limits. Consider splitting: LFS for everything except ISOs; separate store for ISOs.

---

### 11.2 S3-Compatible Object Storage (Minio / Backblaze B2 / Wasabi)

**How it works:** Store each ingested artifact at a key that encodes `name/version/filename`. Enable versioning on the bucket to retain old versions. Retrieve by key.

**Pros:**
- No practical file size limit.
- Bucket versioning is native — retains all versions of an overwritten object.
- Minio is self-hosted and S3-compatible — can run as an LXC on Proxmox (perfect given the Proxmox automation doc).
- Wide tool support; the rebuild VFS layer could be extended with an S3 provider.
- Backblaze B2 is cheap ($6/TB/month) if you want an offsite mirror.
- Built-in ETag (MD5 or SHA-256 depending on config) for integrity.

**Cons:**
- No human-readable history like git — versioning is by object version ID, not a commit log.
- Requires running infrastructure (Minio) or paying a cloud provider.
- Access control requires IAM policies rather than git credentials.

**Verdict:** Best all-around fit for binary artifact storage at scale, especially for large files. Minio on Proxmox fits the existing infrastructure. Add SHA-256 verification in the ingest runner on upload and download.

---

### 11.3 OCI Registry (ORAS / Zot)

**How it works:** OCI (Open Container Initiative) registries store arbitrary blobs — not just container images. The [ORAS](https://oras.land/) project defines conventions for pushing/pulling arbitrary files as OCI artifacts. Zot is a lightweight OCI-native registry (Apache 2.0).

**Pros:**
- Content-addressed by SHA-256 — integrity is structural, not bolted on.
- Versioning via tags (`jdk:21.0.2`, `jdk:21.0.3`); tag history is retained.
- Self-hosted with Zot (single binary, zero config — same philosophy as Bootimus).
- GitHub Container Registry (`ghcr.io`) can store private OCI artifacts at no cost up to 500 MB.
- Growing ecosystem; ORAS CLI has `push` and `pull` commands that the ingest runner could wrap.

**Cons:**
- Unfamiliar mental model for non-container artifacts ("it's just a container registry?").
- File size limits on hosted registries (GitHub: 500 MB per file).
- Less tooling for browsing/managing artifact history than a proper artifact repo.

**Verdict:** Technically elegant and checksum-correct by construction. Best for environments already running container infrastructure. Zot on Proxmox is a viable self-hosted option.

---

### 11.4 ZFS Dataset (Proxmox-local)

**How it works:** Store artifacts in a structured directory on a ZFS dataset (e.g., `local-zfs/artifacts/jdk/21.0.2/`). Use ZFS snapshots for version history. Serve over NFS or HTTP (nginx) to other machines.

**Pros:**
- ZFS provides copy-on-write integrity + checksums at the block level — the strongest per-block integrity guarantee of any option here.
- ZFS snapshots are instant and space-efficient (COW); roll back to any prior state in seconds.
- No additional server software needed; the Proxmox host already has ZFS.
- Serves naturally as the backing store for a Minio instance or a simple nginx file server.

**Cons:**
- Not directly usable as a VFS backend without a serving layer (HTTP/NFS).
- No remote access model out of the box — needs a gateway.
- Not a versioned artifact store; snapshot management is manual.

**Verdict:** Best as the physical storage layer under another serving option (Minio on ZFS = best of both worlds), not as a standalone artifact store.

---

### 11.5 Recommendation

**Primary store:** Minio (S3-compatible) running as an LXC on Proxmox, backed by a ZFS dataset. This covers all artifact sizes including ISOs, gives native bucket versioning, and the existing rebuild VFS layer can be extended with an S3 provider using the `boto3` / `minio` Python SDK.

**Secondary / mirror:** Git LFS on a self-hosted Gitea instance for everything except ISOs (where LFS is impractical). The `.reingest` files already live in a git repo (`rebuild-recipes`); keeping the smaller binaries in LFS alongside them is ergonomically clean.

**Integrity model:**
1. SHA-256 verified at download time (already implemented in the `http` method).
2. SHA-256 stored as S3 object metadata and/or in a sidecar manifest file at upload time.
3. SHA-256 re-verified at retrieval time before any consumer uses the artifact.

This gives end-to-end verifiable provenance: origin URL → checksum at download → checksum in store → checksum at use.
