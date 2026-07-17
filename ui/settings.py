import streamlit as st

from services.settings_service import (
    load_settings,
    save_settings,
    reset_settings,
    get_api_keys,
    save_api_keys,
    mask_key,
    MANAGED_KEYS,
)


def show_settings():

    st.subheader("⚙ Settings")

    st.write(
        "Configure API keys and RAG behaviour for CodePilot AI."
    )

    st.divider()

    # =============================
    # API Keys
    # =============================

    st.markdown("### 🔑 API Keys")

    st.caption(
        "Keys are saved to your local .env file and take effect "
        "immediately - no restart required."
    )

    current_keys = get_api_keys()

    with st.form("api_keys_form"):

        key_inputs = {}

        for field, (env_var, label) in MANAGED_KEYS.items():

            existing = current_keys.get(field, "")

            placeholder = (
                f"Currently set ({mask_key(existing)})"
                if existing
                else "Not set"
            )

            key_inputs[field] = st.text_input(
                label,
                value="",
                type="password",
                placeholder=placeholder,
                help=f"Environment variable: {env_var}"
            )

        st.caption(
            "Leave a field blank to keep its currently saved value."
        )

        keys_submitted = st.form_submit_button(
            "💾 Save API Keys",
            use_container_width=True
        )

        if keys_submitted:

            updated = save_api_keys(**key_inputs)

            if updated:
                st.success(
                    f"Saved: {', '.join(updated)}"
                )
            else:
                st.info(
                    "No changes - all fields were left blank."
                )

    # Quick status readout
    status_cols = st.columns(len(MANAGED_KEYS))

    for col, (field, (env_var, label)) in zip(
        status_cols,
        MANAGED_KEYS.items()
    ):

        with col:

            if current_keys.get(field):
                st.success(f"{label}\n\n✅ Configured")
            else:
                st.warning(f"{label}\n\n⚠ Not set")

    st.divider()

    # =============================
    # RAG / Model Configuration
    # =============================

    st.markdown("### 🧠 Model & Retrieval Configuration")

    settings = load_settings()

    with st.form("rag_settings_form"):

        provider_options = ["auto", "gemini", "mistral"]

        embedding_provider = st.radio(
            "Embedding Provider",
            provider_options,
            index=provider_options.index(
                settings["embedding_provider"]
            ),
            horizontal=True,
            help=(
                "'auto' tries Gemini first and falls back to Mistral "
                "if it fails. Choose a specific provider to lock it."
            )
        )

        llm_temperature = st.slider(
            "LLM Temperature",
            min_value=0.0,
            max_value=1.0,
            value=float(settings["llm_temperature"]),
            step=0.05,
            help="Lower = more focused/deterministic answers. "
                 "Higher = more creative/varied answers."
        )

        st.markdown("**Code Chunking**")

        chunk_col1, chunk_col2 = st.columns(2)

        with chunk_col1:

            chunk_size = st.slider(
                "Chunk Size (characters)",
                min_value=100,
                max_value=2000,
                value=int(settings["chunk_size"]),
                step=50,
                help="Larger chunks give the model more context per "
                     "match but reduce retrieval precision."
            )

        with chunk_col2:

            chunk_overlap = st.slider(
                "Chunk Overlap (characters)",
                min_value=0,
                max_value=500,
                value=int(settings["chunk_overlap"]),
                step=10,
                help="How much consecutive chunks overlap, so context "
                     "isn't lost at chunk boundaries."
            )

        top_k = st.slider(
            "Retrieved Chunks (top-k)",
            min_value=1,
            max_value=20,
            value=int(settings["top_k"]),
            step=1,
            help="How many code chunks are pulled into context for "
                 "each question. Higher = more context, slower/costlier."
        )

        st.caption(
            "⚠ Chunking changes only apply to projects indexed "
            "*after* saving - re-upload/re-index existing projects to "
            "apply a new chunk size."
        )

        rag_submitted = st.form_submit_button(
            "💾 Save Configuration",
            use_container_width=True
        )

        if rag_submitted:

            save_settings({
                "embedding_provider": embedding_provider,
                "llm_temperature": llm_temperature,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "top_k": top_k,
            })

            st.success("Configuration saved.")
            st.rerun()

    st.divider()

    if st.button(
        "↩ Reset to Defaults",
        use_container_width=True
    ):

        reset_settings()
        st.success("Settings reset to defaults.")
        st.rerun()