from transformers.pipelines.text_generation import TextGenerationPipeline, ReturnType
from transformers.utils import is_tf_available, is_torch_available


if is_torch_available():
    from transformers.models.auto.modeling_auto import MODEL_FOR_CAUSAL_LM_MAPPING_NAMES
    from transformers.pipelines.pt_utils import KeyDataset

if is_tf_available():
    import tensorflow as tf

    from transformers.models.auto.modeling_tf_auto import TF_MODEL_FOR_CAUSAL_LM_MAPPING_NAMES



class TextWithLogitsGenerationPipeline(TextGenerationPipeline):
    """
    Rewritten language generation pipeline using any `ModelWithLMHead`. This pipeline does the same thing as the original TextGenerationPipeline while it also outputs logits.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _forward(self, model_inputs, **generate_kwargs):
        input_ids = model_inputs["input_ids"]
        attention_mask = model_inputs.get("attention_mask", None)
        # Allow empty prompts
        if input_ids.shape[1] == 0:
            input_ids = None
            attention_mask = None
            in_b = 1
        else:
            in_b = input_ids.shape[0]
        prompt_text = model_inputs.pop("prompt_text")

        # If there is a prefix, we may need to adjust the generation length. Do so without permanently modifying
        # generate_kwargs, as some of the parameterization may come from the initialization of the pipeline.
        prefix_length = generate_kwargs.pop("prefix_length", 0)
        if prefix_length > 0:
            has_max_new_tokens = "max_new_tokens" in generate_kwargs or (
                "generation_config" in generate_kwargs
                and generate_kwargs["generation_config"].max_new_tokens is not None
            )
            if not has_max_new_tokens:
                generate_kwargs["max_length"] = generate_kwargs.get("max_length") or self.generation_config.max_length
                generate_kwargs["max_length"] += prefix_length
            has_min_new_tokens = "min_new_tokens" in generate_kwargs or (
                "generation_config" in generate_kwargs
                and generate_kwargs["generation_config"].min_new_tokens is not None
            )
            if not has_min_new_tokens and "min_length" in generate_kwargs:
                generate_kwargs["min_length"] += prefix_length

        # User-defined `generation_config` passed to the pipeline call take precedence
        if "generation_config" not in generate_kwargs:
            generate_kwargs["generation_config"] = self.generation_config

        generate_output = self.model.generate(input_ids=input_ids, attention_mask=attention_mask, **generate_kwargs)
        logits = generate_output["logits"]
        generated_sequence = generate_output["sequences"]
        out_b = generated_sequence.shape[0]
        if self.framework == "pt":
            generated_sequence = generated_sequence.reshape(in_b, out_b // in_b, *generated_sequence.shape[1:])
        elif self.framework == "tf":
            generated_sequence = tf.reshape(generated_sequence, (in_b, out_b // in_b, *generated_sequence.shape[1:]))
        return {"generated_sequence": generated_sequence, "input_ids": input_ids, "prompt_text": prompt_text, "logits": logits}

    def postprocess(
        self,
        model_outputs,
        return_type=ReturnType.FULL_TEXT,
        clean_up_tokenization_spaces=True,
        continue_final_message=None,
    ):
        generated_sequence = model_outputs["generated_sequence"][0]
        input_ids = model_outputs["input_ids"]
        prompt_text = model_outputs["prompt_text"]
        logits = model_outputs["logits"]
        generated_sequence = generated_sequence.numpy().tolist()
        records = []
        for sequence in generated_sequence:
            if return_type == ReturnType.TENSORS:
                record = {"generated_token_ids": sequence, "logits": logits}
            elif return_type in {ReturnType.NEW_TEXT, ReturnType.FULL_TEXT}:
                # Decode text
                text = self.tokenizer.decode(
                    sequence,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=clean_up_tokenization_spaces,
                )

                # Remove PADDING prompt of the sequence if XLNet or Transfo-XL model is used
                if input_ids is None:
                    prompt_length = 0
                else:
                    prompt_length = len(
                        self.tokenizer.decode(
                            input_ids[0],
                            skip_special_tokens=True,
                            clean_up_tokenization_spaces=clean_up_tokenization_spaces,
                        )
                    )

                all_text = text[prompt_length:]
                if return_type == ReturnType.FULL_TEXT:
                    if isinstance(prompt_text, str):
                        all_text = prompt_text + all_text
                    elif isinstance(prompt_text, Chat):
                        if continue_final_message is None:
                            # If the user passes a chat ending in an assistant message, we treat it as a prefill by
                            # default because very few models support multiple separate, consecutive assistant messages
                            continue_final_message = prompt_text.messages[-1]["role"] == "assistant"
                        if continue_final_message:
                            # With assistant prefill, concat onto the end of the last message
                            all_text = list(prompt_text.messages)[:-1] + [
                                {
                                    "role": prompt_text.messages[-1]["role"],
                                    "content": prompt_text.messages[-1]["content"] + all_text,
                                }
                            ]
                        else:
                            # When we're not starting from a prefill, the output is a new assistant message
                            all_text = list(prompt_text.messages) + [{"role": "assistant", "content": all_text}]
                record = {"generated_text": all_text, "logits": logits}
            records.append(record)

        return records